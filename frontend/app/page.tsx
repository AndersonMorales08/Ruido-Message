"use client";

import { useState } from "react";
import { 
  UploadCloud, 
  Lock, 
  Unlock,
  FileAudio,
  Key, 
  FileJson, 
  ShieldCheck, 
  Eye,
  RefreshCw
} from "lucide-react";

export default function AudioSteganography() {
  const [activeTab, setActiveTab] = useState<"encode" | "decode">("encode");

  // --- ESTADOS PARA CODIFICAR (ENCODE) ---
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isFinished, setIsFinished] = useState(false);

  // --- ESTADOS PARA DECODIFICAR (DECODE) ---
  const [stegoAudio, setStegoAudio] = useState<File | null>(null);
  const [privateKey, setPrivateKey] = useState<File | null>(null);
  const [huffmanJson, setHuffmanJson] = useState<File | null>(null);
  const [isDecoding, setIsDecoding] = useState(false);
  const [isDecoded, setIsDecoded] = useState(false);
  const [recoveredMessage, setRecoveredMessage] = useState("");

  const ENCRYPT_API = process.env.NEXT_PUBLIC_ENCRYPT_API || 'http://localhost:8000';
  const DECRYPT_API = process.env.NEXT_PUBLIC_DECRYPT_API || 'http://localhost:8001';

  // Simulación: Ocultar Mensaje (Encode)
  const handleProcessEncode = async () => {
    const  formData = new FormData();

    if (!audioFile || !message) return;
    setIsProcessing(true);
    
    if (audioFile) {
      formData.append('audio_file', audioFile);
      formData.append('audio_name', audioFile.name); // Puedes enviar el nombre del archivo o cualquier otro dato necesario
      formData.append('text', message); // Agrega el mensaje a ocultar
    }
    // Aquí iría tu lógica real: Huffman -> RSA -> LSB Embedding

    try {
      const res = await fetch(ENCRYPT_API + '/api/encrypt_compress', {
        method: 'POST',
        // headers: { 'Content-Type': 'application/json' },
        body: formData
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'encriptado_comprimido.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      // setEncryptedData(data.result); // Ajusta la key según tu FastAPI
    } catch (error) {
      console.error('Error al encriptar:', error);
      // setEncryptedData('Error de conexión con el contenedor de encriptación.');
    }

    setTimeout(() => {
      setIsProcessing(false);
      setIsFinished(true);
    }, 2000);
  };

  // Simulación: Revelar Mensaje (Decode)
  const handleProcessDecode = async () => {
    const  formData = new FormData();

    if (!stegoAudio || !privateKey || !huffmanJson) return;
    setIsDecoding(true);

    formData.append('audio_file', stegoAudio);
    formData.append('pem_file', privateKey);
    formData.append('huffman_file', huffmanJson);

    try {
      const res = await fetch(DECRYPT_API + '/api/decrypt_decompress', {
        method: 'POST',
        // headers: { 'Content-Type': 'application/json' },
        body: formData
      });
      const data = await res.json();
      setRecoveredMessage(data?.result || "Mensaje recuperado simulado: ¡Hola, mundo!")
      // setEncryptedData(data.result); // Ajusta la key según tu FastAPI
    } catch (error) {
      console.error('Error al encriptar:', error);
      // setEncryptedData('Error de conexión con el contenedor de encriptación.');
    }

    // Aquí iría tu lógica real: Extraer LSB -> Descifrar RSA -> Descomprimir Huffman
    setTimeout(() => {
      setIsDecoding(false);
      setIsDecoded(true);
    }, 2500);
  };

  const resetEncode = () => {
    setAudioFile(null);
    setMessage("");
    setIsFinished(false);
  };

  const resetDecode = () => {
    setStegoAudio(null);
    setPrivateKey(null);
    setHuffmanJson(null);
    setIsDecoded(false);
    setRecoveredMessage("");
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="w-full max-w-3xl space-y-8">
        
        {/* Encabezado */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 mb-4">
            <ShieldCheck className="h-10 w-10 text-indigo-400" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ruido Message
          </h1>
          <p className="mt-2 text-sm text-neutral-400">
            Esteganografía de audio segura con compresión <span className="text-indigo-400">Huffman</span> y criptografía asimétrica <span className="text-indigo-400">RSA</span>.
          </p>
        </div>

        {/* Selector de Pestañas (Tabs) */}
        <div className="grid grid-cols-2 p-1 bg-neutral-900 border border-neutral-800 rounded-xl">
          <button
            onClick={() => setActiveTab("encode")}
            className={`flex items-center justify-center py-2.5 text-sm font-medium rounded-lg transition-all ${
              activeTab === "encode"
                ? "bg-neutral-800 text-white shadow"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            <Lock className="h-4 w-4 mr-2" />
            Ocultar Mensaje (Encode)
          </button>
          <button
            onClick={() => setActiveTab("decode")}
            className={`flex items-center justify-center py-2.5 text-sm font-medium rounded-lg transition-all ${
              activeTab === "decode"
                ? "bg-neutral-800 text-white shadow"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            <Unlock className="h-4 w-4 mr-2" />
            Revelar Mensaje (Decode)
          </button>
        </div>

        {/* Tarjeta Principal */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl shadow-2xl p-6 sm:p-10 transition-all">
          
          {/* ================= SECCIÓN ENCODE ================= */}
          {activeTab === "encode" && (
            !isFinished ? (
              <div className="space-y-6">
                {/* 1. Subir Audio Base */}
                <div>
                  <label className="block text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                    1. Archivo de Audio Base
                  </label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-neutral-800 border-dashed rounded-xl hover:border-indigo-500/50 transition-colors bg-neutral-950/40">
                    <div className="space-y-1 text-center">
                      <UploadCloud className="mx-auto h-10 w-10 text-neutral-500" />
                      <div className="flex text-sm text-neutral-400 justify-center">
                        <label htmlFor="audio-upload" className="relative cursor-pointer rounded-md font-medium text-indigo-400 hover:text-indigo-300 focus-within:outline-none">
                          <span>Sube un archivo</span>
                          <input id="audio-upload" type="file" accept="audio/*,.wav,.mp3,.m4a,.flac,.ogg,.aac" className="sr-only" onChange={(e) => setAudioFile(e.target.files?.[0] || null)} />
                        </label>
                        <p className="pl-1">o arrastra y suelta</p>
                      </div>
                      <p className="text-xs text-neutral-500">
                        {audioFile ? `Seleccionado: ${audioFile.name}` : "Formato WAV (Recomendado)"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 2. Mensaje Secreto */}
                <div>
                  <label htmlFor="message" className="block text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                    2. Mensaje a ocultar
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 pt-3 pointer-events-none">
                      <Lock className="h-5 w-5 text-neutral-600" />
                    </div>
                    <textarea
                      id="message"
                      rows={4}
                      className="block w-full pl-11 pr-4 py-3 border border-neutral-800 rounded-xl bg-neutral-950 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm"
                      placeholder="Este mensaje será comprimido con Huffman y cifrado con RSA..."
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                    />
                  </div>
                </div>

                {/* Botón Ejecutar */}
                <button
                  onClick={handleProcessEncode}
                  disabled={!audioFile || !message || isProcessing}
                  className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white transition-all ${
                    !audioFile || !message || isProcessing
                      ? "bg-neutral-800 cursor-not-allowed text-neutral-500"
                      : "bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-neutral-900"
                  }`}
                >
                  {isProcessing ? (
                    <span className="flex items-center">
                      <RefreshCw className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
                      Procesando, comprimiendo y cifrando...
                    </span>
                  ) : (
                    "Ocultar Mensaje en Audio"
                  )}
                </button>
              </div>
            ) : (
              /* Resultados de la Codificación */
              <div className="space-y-6 text-center animate-in fade-in zoom-in duration-350">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-indigo-500/10 border border-indigo-500/20">
                  <ShieldCheck className="h-8 w-8 text-indigo-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">¡Mensaje Ocultado con Éxito!</h2>
                  <p className="text-neutral-400 text-lg mt-1">
                    Se ha descargado el archivo ZIP con el mensaje oculto, la llave privada y el árbol de Huffman.
                  </p>
                </div>


                <div className="pt-6 border-t border-neutral-800">
                  <button 
                    onClick={resetEncode}
                    className="text-sm text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center"
                  >
                    ← Ocultar otro mensaje
                  </button>
                </div>
              </div>
            )
          )}

          {/* ================= SECCIÓN DECODE ================= */}
          {activeTab === "decode" && (
            !isDecoded ? (
              <div className="space-y-6">
                
                {/* Inputs de Descifrado */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  
                  {/* 1. Subir Audio con Mensaje Oculto */}
                  <div className="flex flex-col">
                    <label className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                      1. Audio Portador
                    </label>
                    <div className="flex-1 flex flex-col items-center justify-center p-4 border border-neutral-800 rounded-xl bg-neutral-950/40 hover:border-neutral-700 transition-colors text-center relative cursor-pointer min-h-[140px]">
                      <input type="file" accept="audio/wav" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setStegoAudio(e.target.files?.[0] || null)} />
                      <FileAudio className={`h-8 w-8 mb-2 ${stegoAudio ? 'text-indigo-400' : 'text-neutral-600'}`} />
                      <span className="text-xs font-medium text-neutral-300">
                        {stegoAudio ? stegoAudio.name : "Subir stego_audio.wav"}
                      </span>
                    </div>
                  </div>

                  {/* 2. Subir Llave Privada PEM */}
                  <div className="flex flex-col">
                    <label className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                      2. Llave Privada (.pem)
                    </label>
                    <div className="flex-1 flex flex-col items-center justify-center p-4 border border-neutral-800 rounded-xl bg-neutral-950/40 hover:border-neutral-700 transition-colors text-center relative cursor-pointer min-h-[140px]">
                      <input type="file" accept=".pem" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setPrivateKey(e.target.files?.[0] || null)} />
                      <Key className={`h-8 w-8 mb-2 ${privateKey ? 'text-amber-400' : 'text-neutral-600'}`} />
                      <span className="text-xs font-medium text-neutral-300">
                        {privateKey ? privateKey.name : "Subir private_key.pem"}
                      </span>
                    </div>
                  </div>

                  {/* 3. Subir Diccionario Huffman */}
                  <div className="flex flex-col">
                    <label className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                      3. Árbol Huffman (.json)
                    </label>
                    <div className="flex-1 flex flex-col items-center justify-center p-4 border border-neutral-800 rounded-xl bg-neutral-950/40 hover:border-neutral-700 transition-colors text-center relative cursor-pointer min-h-[140px]">
                      <input type="file" accept=".json" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setHuffmanJson(e.target.files?.[0] || null)} />
                      <FileJson className={`h-8 w-8 mb-2 ${huffmanJson ? 'text-emerald-400' : 'text-neutral-600'}`} />
                      <span className="text-xs font-medium text-neutral-300">
                        {huffmanJson ? huffmanJson.name : "Subir huffman_tree.json"}
                      </span>
                    </div>
                  </div>

                </div>

                {/* Botón Ejecutar Descifrado */}
                <button
                  onClick={handleProcessDecode}
                  disabled={!stegoAudio || !privateKey || !huffmanJson || isDecoding}
                  className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white transition-all ${
                    !stegoAudio || !privateKey || !huffmanJson || isDecoding
                      ? "bg-neutral-800 cursor-not-allowed text-neutral-500"
                      : "bg-emerald-600 hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 focus:ring-offset-neutral-900"
                  }`}
                >
                  {isDecoding ? (
                    <span className="flex items-center">
                      <RefreshCw className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
                      Extrayendo bits, descifrando RSA y descomprimiendo...
                    </span>
                  ) : (
                    "Descifrar y Revelar Mensaje"
                  )}
                </button>

              </div>
            ) : (
              /* Mensaje Decodificado Exitosamente */
              <div className="space-y-6 animate-in fade-in zoom-in duration-350">
                <div className="text-center">
                  <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-4">
                    <Eye className="h-8 w-8 text-emerald-400" />
                  </div>
                  <h2 className="text-xl font-bold text-white">¡Mensaje Recuperado!</h2>
                  <p className="text-neutral-400 text-sm mt-1">
                    El proceso de extracción, descifrado asimétrico y descompresión Huffman finalizó con éxito.
                  </p>
                </div>

                {/* Caja de Texto del Mensaje Extraído */}
                <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-5 relative">
                  <div className="absolute top-3 right-3 text-xs text-neutral-600 font-mono">
                    RECOVERED_DATA
                  </div>
                  <p className="text-sm font-mono text-emerald-400 leading-relaxed whitespace-pre-wrap">
                    {recoveredMessage}
                  </p>
                </div>

                <div className="pt-6 border-t border-neutral-800 text-center">
                  <button 
                    onClick={resetDecode}
                    className="text-sm text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center"
                  >
                    ← Descifrar otro archivo
                  </button>
                </div>
              </div>
            )
          )}

        </div>
      </div>
    </div>
  );
}

// 'use client';

// import { useState } from 'react';

// export default function Home() {
//   const [message, setMessage] = useState('');
//   const [encryptedData, setEncryptedData] = useState('');
//   const [decryptedMessage, setDecryptedMessage] = useState('');
//   const [loading, setLoading] = useState(false);

//   // Estas URLs vendrán de tus variables de entorno, apuntando a los puertos expuestos de FastAPI
//   const ENCRYPT_API = process.env.NEXT_PUBLIC_ENCRYPT_API || 'http://localhost:8000';
//   const DECRYPT_API = process.env.NEXT_PUBLIC_DECRYPT_API || 'http://localhost:8001';

//   const handleEncrypt = async () => {
//     if (!message) return;
//     setLoading(true);
//     try {
//       const res = await fetch(ENCRYPT_API + '/api/encrypt_compress' + `?text=${message}`, {
//         method: 'GET',
//         headers: { 'Content-Type': 'application/json' },
//       });
//       const data = await res.json();
//       setEncryptedData(data.result); // Ajusta la key según tu FastAPI
//     } catch (error) {
//       console.error('Error al encriptar:', error);
//       setEncryptedData('Error de conexión con el contenedor de encriptación.');
//     }
//     setLoading(false);
//   };

//   const handleDecrypt = async () => {
//     if (!encryptedData) return;
//     setLoading(true);
//     try {
//       const res = await fetch(DECRYPT_API + '/api/decrypt_decompress', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ encrypted_text: encryptedData }),
//       });
//       const data = await res.json();
//       setDecryptedMessage(data.decrypted_text); // Ajusta la key según tu FastAPI
//     } catch (error) {
//       console.error('Error al desencriptar:', error);
//       setDecryptedMessage('Error de conexión con el contenedor de desencriptación.');
//     }
//     setLoading(false);
//   };

//   return (
//     <main className="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
//       <div className="max-w-4xl mx-auto bg-white p-8 rounded-2xl shadow-xl">
//         <h1 className="text-3xl font-bold mb-2 text-center text-indigo-600">
//           Ruido Message
//         </h1>
//         <p className="text-center text-gray-500 mb-8">
//           Fase 1: Pruebas de Compresión y Encriptación (Sin Audio)
//         </p>

//         {/* Zona de Audio (Deshabilitada temporalmente) */}
//         <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 mb-8 text-center bg-gray-50 opacity-60">
//           <p className="text-sm font-semibold text-gray-500 mb-2">🎵 Archivo de Audio (Próximamente)</p>
//           <input type="file" disabled className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 disabled:cursor-not-allowed" />
//           <p className="text-xs text-gray-400 mt-2">La esteganografía se implementará en la siguiente fase.</p>
//         </div>

//         <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
//           {/* Columna Izquierda: Encriptación */}
//           <div className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium mb-1">Mensaje Secreto a Ocultar</label>
//               <textarea
//                 className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
//                 rows={4}
//                 value={message}
//                 onChange={(e) => setMessage(e.target.value)}
//                 placeholder="Escribe el mensaje aquí..."
//               />
//             </div>
//             <button
//               onClick={handleEncrypt}
//               disabled={loading || !message}
//               className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400"
//             >
//               Comprimir y Encriptar
//             </button>
//             <div>
//               <label className="block text-sm font-medium mb-1">Resultado Encriptado (Base64/Hex)</label>
//               <textarea
//                 className="w-full p-3 border border-gray-300 rounded-lg bg-gray-100 font-mono text-xs text-gray-600 outline-none"
//                 rows={4}
//                 value={encryptedData}
//                 readOnly
//                 placeholder="Aquí aparecerá la data encriptada..."
//               />
//             </div>
//           </div>

//           {/* Columna Derecha: Desencriptación */}
//           <div className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium mb-1 text-gray-400">Data a Procesar (Simulando extracción del audio)</label>
//               <textarea
//                 className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 font-mono text-xs text-gray-500 outline-none"
//                 rows={4}
//                 value={encryptedData}
//                 readOnly
//               />
//             </div>
//             <button
//               onClick={handleDecrypt}
//               disabled={loading || !encryptedData}
//               className="w-full bg-emerald-600 text-white py-3 rounded-lg font-semibold hover:bg-emerald-700 transition disabled:bg-gray-400"
//             >
//               Desencriptar y Descomprimir
//             </button>
//             <div>
//               <label className="block text-sm font-medium mb-1">Mensaje Recuperado</label>
//               <textarea
//                 className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 bg-emerald-50 text-emerald-900 outline-none font-medium"
//                 rows={4}
//                 value={decryptedMessage}
//                 readOnly
//                 placeholder="Aquí aparecerá el mensaje original..."
//               />
//             </div>
//           </div>
//         </div>
//       </div>
//     </main>
//   );
// }