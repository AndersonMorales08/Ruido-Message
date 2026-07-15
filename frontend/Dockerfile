# 1. Usamos una imagen ligera de Node.js
FROM node:20-alpine

# 2. Creamos y definimos el directorio de trabajo
WORKDIR /app

# 3. Copiamos los archivos de dependencias primero (para aprovechar la caché de Docker)
COPY package*.json ./

# 4. Instalamos las dependencias
RUN npm install

# 5. Copiamos el resto del código fuente del frontend
COPY . .

# 6. Compilamos la aplicación de Next.js
RUN npm run build

# 7. Exponemos el puerto en el que corre Next.js por defecto
EXPOSE 3000

# 8. Arrancamos la aplicación en modo producción
CMD ["npm", "start"]