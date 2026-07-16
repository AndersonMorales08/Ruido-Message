# Ruido Message
## Integrantes
- Lina Sofia Espinal Daza
- Anderson David Morales Chila

## Descripción
Proyecto de esteganografía de audio que esconde un mensaje cifrado en RSA y comprimido con el algoritmo de Huffman dentro de cualquier archivo de audio. Se usaron los lenguajes de Matlab, Python y Next.js con Typescript.

## Ejecución del proyecto

### Requisitos
Tener ***Docker*** instalado.

### Instrucciones de ejecución
1. Ejecutar el siguiente comando:
``` bash
docker compose up --build
```
2. Ir a la dirección [http://localhost:3000](http://localhost:3000).

## Estructura del proyecto 
```
Ruido-Message
├─ README.md
├─ descencriptar_descompresion
│  ├─ +descencriptacion_rsa
│  │  ├─ def_rsa.m
│  │  ├─ descifrado_rsa.m
│  │  └─ modpow.m
│  ├─ +descompresion_huffman
│  │  └─ huffmanDescomprimir.m
│  ├─ Dockerfile
│  ├─ PythonPackage1
│  │  └─ output
│  │     ├─ build
│  │     │  ├─ GettingStarted.html
│  │     │  ├─ Matlab_DD
│  │     │  │  ├─ Matlab_DD.ctf
│  │     │  │  └─ __init__.py
│  │     │  ├─ buildresult.json
│  │     │  ├─ includedSupportPackages.txt
│  │     │  ├─ pyproject.toml
│  │     │  ├─ readme.txt
│  │     │  ├─ requiredMCRProducts.txt
│  │     │  ├─ setup.py
│  │     │  └─ unresolvedSymbols.txt
│  │     └─ package
│  ├─ app.py
│  ├─ descencriptar_descompresion.m
│  ├─ descencriptar_descompresion.prj
│  ├─ requirements.txt
│  └─ resources
│     └─ project
│        └─ ...
├─ docker-compose.yaml
├─ encriptar_compresion
│  ├─ +compresion_huffman
│  │  ├─ construirArbol.m
│  │  ├─ huffmanComprimir.m
│  │  └─ recorrerArbol.m
│  ├─ +encriptacion_rsa
│  │  ├─ cifrado_rsa.m
│  │  ├─ def_rsa.m
│  │  ├─ esPrimoMillerRabin.m
│  │  ├─ generador_primos.m
│  │  └─ modpow.m
│  ├─ Dockerfile
│  ├─ PythonPackage1
│  │  └─ output
│  │     ├─ build
│  │     │  ├─ GettingStarted.html
│  │     │  ├─ Matlab_EC
│  │     │  │  ├─ Matlab_EC.ctf
│  │     │  │  └─ __init__.py
│  │     │  ├─ buildresult.json
│  │     │  ├─ includedSupportPackages.txt
│  │     │  ├─ pyproject.toml
│  │     │  ├─ readme.txt
│  │     │  ├─ requiredMCRProducts.txt
│  │     │  ├─ setup.py
│  │     │  └─ unresolvedSymbols.txt
│  │     └─ package
│  │        └─ deploymentLog.html
│  ├─ app.py
│  ├─ encriptar_compresion.m
│  ├─ encriptar_compresion.prj
│  ├─ esteganografia_audio.py
│  ├─ requirements.txt
│  └─ resources
│     └─ project
│        └─ ... 
└─ frontend
   ├─ AGENTS.md
   ├─ CLAUDE.md
   ├─ Dockerfile
   ├─ README.md
   ├─ app
   │  ├─ api
   │  │  ├─ decode
   │  │  │  └─ route.ts
   │  │  └─ encode
   │  │     └─ route.ts
   │  ├─ favicon.ico
   │  ├─ globals.css
   │  ├─ layout.tsx
   │  └─ page.tsx
   ├─ package.json
   ├─ public
   │  ├─ file.svg
   │  ├─ globe.svg
   │  ├─ next.svg
   │  ├─ vercel.svg
   │  └─ window.svg
   ├─ script.js
   └─ tsconfig.json

```