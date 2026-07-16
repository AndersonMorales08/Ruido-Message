# 1. Usar la imagen oficial del MATLAB Runtime de MathWorks como base.
# IMPORTANTE: Reemplaza 'r2026a' por la versión exacta de tu MATLAB (ej. r2025a, r2024b, etc.)
FROM containers.mathworks.com/matlab-runtime:r2025b

# 2. Cambiar temporalmente a root para instalar herramientas del sistema
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Evitar bloqueos de entornos administrados (PEP 668) en distribuciones Linux modernas
ENV PIP_BREAK_SYSTEM_PACKAGES=1

ENV LD_LIBRARY_PATH=/opt/matlab/matlabruntime/R2025b/runtime/glnxa64:\
/opt/matlab/matlabruntime/R2025b/bin/glnxa64:\
/opt/matlab/matlabruntime/R2025b/sys/os/glnxa64:\
/opt/matlabruntime/R2025b/runtime/glnxa64:\
/opt/matlabruntime/R2025b/bin/glnxa64:\
/opt/matlabruntime/v252/runtime/glnxa64:\
/usr/local/MATLAB/MATLAB_Runtime/v252/runtime/glnxa64

ENV PYTHONUNBUFFERED=1

ENV AGREE_TO_MATLAB_RUNTIME_LICENSE=YES
# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar los archivos de requerimientos y la lógica de la API
COPY requirements.txt .
COPY app.py .

# 5. Copiar la carpeta 'build' (que extrajiste del output de MATLAB)
COPY /PythonPackage1/output/build/ ./build

# 6. Instalar dependencias de Python y el paquete nativo compilado de MATLAB
RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir ./build

# Exponer el puerto por el que escuchará FastAPI
EXPOSE 8000

# 7. Comando definitivo para correr el servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]