from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import Matlab_DD
import matlab

from esteganografia_audio import PayloadNoEncontradoError, extraer_payload_de_wav

matlab_api = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Liberar memoria de forma limpia al apagar el contenedor
    if matlab_api:
        matlab_api.terminate()


app = FastAPI(title="Esteganografía en audio - Revelar mensaje", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    print("Iniciando MATLAB Runtime en segundo plano...")
    matlab_api = Matlab_DD.initialize()
    print("MATLAB Runtime cargado correctamente.")
    
except Exception as e:
    print(f"Error crítico al inicializar el entorno de MATLAB: {e}")


@app.get("/api/decrypt_decompress")
def decrypt_decompress(message_encrypt: list[int]):
    """Endpoint heredado. Se deja por compatibilidad, pero ya no es
    suficiente por sí solo: descencriptar_descompresion.m ahora también
    necesita la llave privada, n, el diccionario Huffman y la longitud
    original del mensaje (ver /api/revelar_mensaje)."""
    raise HTTPException(
        status_code=410,
        detail="Usa /api/revelar_mensaje, que ya incluye todo lo necesario para descifrar.",
    )


@app.post("/api/revelar_mensaje")
async def revelar_mensaje(llave_privada: int = Form(...), audio: UploadFile = File(...)):
    """
    Recibe un audio WAV con un mensaje escondido y la llave privada RSA.
    1) Extrae del audio el mensaje cifrado + los metadatos (diccionario
       Huffman, n, longitud original) que se escondieron junto con él.
    2) Descifra con RSA y descomprime con Huffman (MATLAB).
    3) Devuelve el mensaje original en texto plano.
    """
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")

    if not audio.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="El audio debe ser un archivo .wav.")

    audio_bytes = await audio.read()

    try:
        payload = extraer_payload_de_wav(audio_bytes)
    except PayloadNoEncontradoError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el audio: {str(e)}")

    try:
        secret_m = matlab.double([payload["secret"]])
        codigos_simbolos_m = matlab.double([payload["codigos_simbolos"]])
        codigos_valores = payload["codigos_valores"]  # lista de strings

        mensaje_recuperado = matlab_api.descencriptar_descompresion(
            secret_m,
            matlab.double(llave_privada),
            matlab.double(payload["n"]),
            codigos_simbolos_m,
            codigos_valores,
            matlab.double(payload["longitud_original"]),
            nargout=1,
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=(
                "No se pudo descifrar el mensaje. Revisa que la llave privada "
                f"sea correcta. Detalle: {str(e)}"
            ),
        )

    return {"status": "success", "mensaje": str(mensaje_recuperado)}