import base64
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import Matlab_EC
import matlab

from esteganografia_audio import (
    CapacidadInsuficienteError,
    ocultar_payload_en_wav,
)

matlab_api = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Liberar memoria de forma limpia al apagar el contenedor
    if matlab_api:
        matlab_api.terminate()


app = FastAPI(title="Esteganografía en audio - Ocultar mensaje", lifespan=lifespan)

# Necesario para que el frontend (servido en otro origen/puerto) pueda llamar a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    print("Iniciando MATLAB Runtime en segundo plano...")
    matlab_api = Matlab_EC.initialize()
    print("MATLAB Runtime cargado correctamente.")
    
except Exception as e:
    print(f"Error crítico al inicializar el entorno de MATLAB: {e}")


def _map_a_dict(codigos) -> dict:
    """Normaliza lo que devuelve encriptacion_compresion.m para el
    diccionario de Huffman (containers.Map) a un dict de Python
    {simbolo_ascii: codigo_binario_str}.

    Según cómo el runtime de MATLAB Compiler SDK exponga el Map hacia
    Python, puede llegar ya como dict, o como un objeto con .keys()/.values().
    Este helper cubre ambos casos.
    """
    if isinstance(codigos, dict):
        return {int(k): str(v) for k, v in codigos.items()}
    # Objeto tipo Map de MATLAB expuesto a Python
    return {int(k): str(v) for k, v in zip(codigos.keys(), codigos.values())}


@app.get("/api/encrypt_compress")
def encrypt_compress(message: str):
    """Endpoint original: solo cifra/comprime, sin esconder en audio."""
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")
    
    try:
        data = matlab.string(message)
        secret, codigos, ky_pub, ky_pr, n = matlab_api.encriptacion_compresion(data, nargout=5)
        return {
            "status": "success",
            "secret": list(secret),
            "codigos": _map_a_dict(codigos),
            "llave_publica": {"e": int(ky_pub), "n": int(n)},
            "llave_privada": {"d": int(ky_pr), "n": int(n)},
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MATLAB: {str(e)}")


@app.post("/api/ocultar_mensaje")
async def ocultar_mensaje(mensaje: str = Form(...), audio: UploadFile = File(...)):
    """
    Recibe un mensaje de texto y un audio WAV.
    1) Comprime el mensaje con Huffman y lo cifra con RSA (MATLAB).
    2) Esconde el resultado dentro del audio (LSB), sin alterarlo audiblemente.
    3) Devuelve el audio con el mensaje escondido (en base64) y la llave
       privada RSA, que el usuario debe guardar aparte para poder
       revelar el mensaje después (NO se esconde en el audio).
    """
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")

    if not audio.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="El audio debe ser un archivo .wav (PCM sin pérdida).")

    if not mensaje.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    audio_bytes = await audio.read()

    try:
        data = matlab.string(mensaje)
        secret, codigos, ky_pub, ky_pr, n = matlab_api.encriptacion_compresion(data, nargout=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MATLAB al cifrar/comprimir: {str(e)}")

    try:
        stego_wav = ocultar_payload_en_wav(
            audio_bytes=audio_bytes,
            secret=list(secret),
            codigos=_map_a_dict(codigos),
            longitud_original=len(mensaje),
            n=int(n),
        )
    except CapacidadInsuficienteError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al esconder el mensaje en el audio: {str(e)}")

    return {
        "status": "success",
        "audio_base64": base64.b64encode(stego_wav).decode("ascii"),
        "nombre_archivo": f"stego_{audio.filename}",
        "llave_privada": int(ky_pr),
        "n": int(n),
        "aviso": (
            "Guarda la llave privada: sin ella nadie (ni tú) podrá revelar el "
            "mensaje escondido en el audio. No la compartas por el mismo canal "
            "que el audio."
        ),
    }