from fastapi import FastAPI, HTTPException
import Matlab_EC
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
    matlab_api = Matlab_EC.initialize()
    print("MATLAB Runtime cargado correctamente.")

except Exception as e:
    print(f"Error cítico al inicializar el entorno de MATLAB: {e}")

@app.get("/api/encrypt_compress")
def encrypt_compress(message: str):
    if not matlab_api:
        raise HTTPException(status_code=500, detail="El servicio de MATLAB no está disponible.")
    
    try:
        data = matlab.string(message)
        result = matlab_api.encriptacion_compresion(data)

        return {
            "status": "success",
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MATLAB: {str(e)}")