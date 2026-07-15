import os
import io
import zipfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse  # 1. Importar el middleware
import Matlab_EC
import traceback
from pydub import AudioSegment

import json
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando servicio de encriptación y compresión...")
    yield
    # Liberar memoria de forma limpia al apagar el contenedor
    if matlab_api:
        matlab_api.terminate()
    print("Servicio de encriptación y compresión apagado.")

app = FastAPI(title="MATLAB Docker API", lifespan=lifespan)

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
    matlab_api = Matlab_EC.initialize()
    print("MATLAB Runtime cargado correctamente.")

except Exception as e:
    print(f"Error crítico al inicializar el entorno de MATLAB: {e}")

@app.post("/api/encrypt_compress")
async def encrypt_compress(audio_file: UploadFile = File(...), text: str = Form(...),
    audio_name: str = Form(...)):
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")
    
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo no es un audio.")
    
    ext = os.path.splitext(audio_name)[1].lower()
    temp_input_path = f"/tmp/temp_uploaded{ext}"
    wav_converted_path = "/tmp/converted_for_matlab.wav"
    wav_output_path = "/tmp/audio_secreto_rsa.wav"
    
    try:
        print(f"Recibido texto: {text}")

        with open(temp_input_path, "wb") as buffer:
            buffer.write(await audio_file.read())

        try:
            # pydub detecta automáticamente si es MP3, M4A, FLAC, etc. usando FFMPEG
            audio = AudioSegment.from_file(temp_input_path)
            # Exportamos como WAV limpio (PCM de 16 bits a 44100Hz o su frecuencia original)
            audio.export(wav_converted_path, format="wav")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"El formato de audio no es compatible o está dañado: {str(e)}")

        try:
            zip_buffer = io.BytesIO()

            secret, codigos, ky_pub, ky_pr, n = matlab_api.encriptar_compresion(text, wav_converted_path, wav_output_path, nargout=5)
            secret = secret[0] if isinstance(secret, list) else secret
            codigos = json.loads(codigos)
            ky_pub = int(ky_pub)
            ky_pr = int(ky_pr)
            n = int(n)  

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Añadir el archivo de audio generado
                zip_file.write(wav_output_path, arcname="audio_secreto_rsa.wav")    

                archivo_pem = f"-----BEGIN PRIVATE KEY-----\n{ky_pr}\n-----END PRIVATE KEY-----\n"
                archivo_pem += f"\n-----BEGIN PUBLIC KEY-----\n{ky_pub}\n-----END PUBLIC KEY-----\n"
                archivo_pem += f"\n-----BEGIN MODULUS-----\n{n}\n-----END MODULUS-----\n"
                archivo_pem += f"\n-----BEGIN SECRET-----\n{secret}\n-----END SECRET-----\n"
                archivo_pem += f"\n-----BEGIN ORIGINAL MESSAGE-----\n{text}\n-----END ORIGINAL MESSAGE-----\n"

                zip_file.writestr("keys_and_secret.pem", archivo_pem)

                zip_file.writestr("huffman_codes.json", json.dumps(codigos, indent=4))

            zip_buffer.seek(0)
                            

            result = str(secret) + "\n" + str(codigos) + "\n" + str(ky_pub) + "\n" + str(ky_pr) + "\n" + str(n)
            print(f"Resultado de MATLAB: {result}")
        
            # return {
            #     "result": result,
            #     "status": "success"   
            # }
        
        except Exception as e:
            # Esto obligará a Docker a escupir el error real en la terminal:
            print("--- ERROR DETECTADO EN LA EJECUCIÓN DE MATLAB ---")
            traceback.print_exc() 
            print("-------------------------------------------------")
            
            raise HTTPException(status_code=500, detail=f"Error en MATLAB: {str(e)}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="encriptado_comprimido.zip"'}
        )
    
    finally:
        # Limpieza de archivos temporales para no saturar el disco del contenedor
        for path in [temp_input_path, wav_converted_path]:
            if os.path.exists(path):
                os.remove(path)