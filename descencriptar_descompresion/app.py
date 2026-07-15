import json
import os
import traceback

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import Matlab_DD
import matlab

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando servicio de descifrado y descompresión...")
    yield
    # Liberar memoria de forma limpia al apagar el contenedor
    if matlab_api:
        matlab_api.terminate()
    print("Servicio de descifrado y descompresión apagado.")

app = FastAPI(title="MATLAB Docker API Descifrado y Descompresión", lifespan=lifespan)

# 2. Configurar los orígenes permitidos
# Puedes poner ["*"] para permitir cualquier origen (útil en desarrollo)
# o la URL específica de tu Next.js, por ejemplo: ["http://localhost:3000"]
origins = [
    "*" 
]

# 3. Añadir el middleware a la aplicación
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

try:
    print("Iniciando MATLAB Runtime en segundo plano...")
    matlab_api = Matlab_DD.initialize()
    print("MATLAB Runtime cargado correctamente.")

except Exception as e:
    print(f"Error crítico al inicializar el entorno de MATLAB: {e}")

@app.post("/api/decrypt_decompress")
async def decrypt_decompress(audio_file: UploadFile = File(...), pem_file: UploadFile = File(...), huffman_file: UploadFile = File(...)):
    
    if not matlab_api:
        print("El servicio de MATLAB no está disponible.")
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")
    
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo no es un audio.")
    
    wav_input_path = f"/tmp/{audio_file.filename}.wav"
    
    try:

        with open(wav_input_path, "wb") as buffer:
            buffer.write(await audio_file.read())

        
        datos_pem = {}
        pem_bytes = await pem_file.read()
        pem_text = pem_bytes.decode("utf-8")

        for linea in pem_text.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            elif "-----BEGIN PUBLIC KEY" in linea or "-----END PUBLIC KEY" in linea or \
               "-----BEGIN MODULUS" in linea or "-----END MODULUS" in linea or \
               "-----BEGIN SECRET" in linea or "-----END SECRET" in linea or \
               "-----BEGIN ORIGINAL MESSAGE" in linea or "-----END ORIGINAL MESSAGE" in linea or \
               "-----BEGIN PRIVATE KEY" in linea or "-----END PRIVATE KEY" in linea:
                continue

            else:
                if "PRIVATE KEY" not in datos_pem:
                    datos_pem["PRIVATE KEY"] = float(linea)
                elif "PUBLIC KEY" not in datos_pem:
                    datos_pem["PUBLIC KEY"] = float(linea)
                elif "MODULUS" not in datos_pem:
                    datos_pem["MODULUS"] = float(linea)
                elif "SECRET" not in datos_pem:
                    datos_pem["SECRET"] = linea
                    datos_temp = datos_pem["SECRET"][1:-1]  # Eliminar los corchetes
                    datos_temp = datos_temp[1:-1].split(",")  # Dividir por comas
                    datos_pem["SECRET"] = matlab.double([float(dato.strip()) for dato in datos_temp])  # Convertir a float y luego a matlab.double
                elif "ORIGINAL MESSAGE" not in datos_pem:
                    datos_pem["ORIGINAL MESSAGE"] = linea


        required_keys = ["SECRET", "PUBLIC KEY", "MODULUS", "ORIGINAL MESSAGE"]
        missing_keys = [key for key in required_keys if key not in datos_pem]
        if missing_keys:
            raise ValueError(f"El archivo PEM no tiene una estructura válida. Faltan: {', '.join(missing_keys)}")

        

        huffman_bytes = await huffman_file.read()
        huffman_data = json.loads(huffman_bytes)

        print(f"datos_pem['PRIVATE KEY']: {datos_pem['PRIVATE KEY']} Tipo: {type(datos_pem['PRIVATE KEY'])}")
        print(f"datos_pem['SECRET']: {datos_pem['SECRET']} Tipo: {type(datos_pem['SECRET'])}")
        print(f"datos_pem['PUBLIC KEY']: {datos_pem['PUBLIC KEY']} Tipo: {type(datos_pem['PUBLIC KEY'])}")
        print(f"datos_pem['MODULUS']: {datos_pem['MODULUS']} Tipo: {type(datos_pem['MODULUS'])}")
        print(f"datos_pem['ORIGINAL MESSAGE']: {datos_pem['ORIGINAL MESSAGE']} Tipo: {type(datos_pem['ORIGINAL MESSAGE'])}")

        huffman_data_new = {}
        
        for key, value in huffman_data.items():
            huffman_data_new['x' + key] = huffman_data[key]

        json_huffman = json.dumps(huffman_data_new, indent=4)
        
        print(json_huffman)
        
        result = matlab_api.descencriptar_descompresion(datos_pem["SECRET"], datos_pem["PUBLIC KEY"], datos_pem["MODULUS"], json_huffman, datos_pem["ORIGINAL MESSAGE"], wav_input_path)

        print(f"Resultado de descifrado y descompresión: {result}")

        return {
            "status": "success",
            "result": result
        }
    
    except Exception as e:
        print("--- ERROR DETECTADO EN LA EJECUCIÓN DE MATLAB ---")
        traceback.print_exc() 
        print("-------------------------------------------------")

        raise HTTPException(status_code=500, detail=f"Error en MATLAB: {str(e)}")
    
    finally:
        # Limpieza de archivos temporales para no saturar el disco del contenedor
        for path in [wav_input_path]:
            if os.path.exists(path):
                os.remove(path)