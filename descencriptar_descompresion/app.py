from fastapi import FastAPI, HTTPException
import Matlab_DD
import matlab

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Liberar memoria de forma limpia al apagar el contenedor
    if matlab_api:
        matlab_api.terminate()

app = FastAPI(title="MATLAB Docker API", lifespan=lifespan)

try:
    print("Iniciando MATLAB Runtime en segundo plano...")
    matlab_api = Matlab_DD.initialize()
    print("MATLAB Runtime cargado correctamente.")

except Exception as e:
    print(f"Error cítico al inicializar el entorno de MATLAB: {e}")

@app.get("/api/decrypt_decompress")
def decrypt_decompress(message_encrypt: list[int]):
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")
    
    try:
        data = matlab.double([message_encrypt])
        result = matlab_api.descencriptar_descompresion(data)

        return {
            "status": "success",
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MATLAB: {str(e)}")