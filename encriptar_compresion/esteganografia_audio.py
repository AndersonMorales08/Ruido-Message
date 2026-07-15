"""
esteganografia_audio.py
------------------------
Esconde y extrae información dentro de archivos de audio WAV usando la
técnica de LSB (Least Significant Bit): se reemplaza el bit menos
significativo de cada muestra de audio PCM por un bit del mensaje a
esconder. El cambio es inaudible porque el bit menos significativo
representa una variación mínima de amplitud (ruido imperceptible).

Este módulo NO cifra ni comprime nada: solo esconde y recupera bytes.
El cifrado (RSA) y la compresión (Huffman) ya existen en el proyecto
(carpetas +encriptacion_rsa / +compresion_huffman en MATLAB); aquí lo
que se esconde es el resultado (el "payload") de ese proceso.

Payload que viajará escondido dentro del audio (todo lo que el
receptor necesita para reconstruir el mensaje, EXCEPTO la llave
privada RSA, que debe compartirse por un canal separado):

{
    "secret": [ ...enteros, el mensaje cifrado con RSA... ],
    "codigos_simbolos": [ ...enteros, símbolos ASCII del diccionario Huffman... ],
    "codigos_valores": [ ...strings, código binario de cada símbolo... ],
    "longitud_original": int,   # número de caracteres del mensaje original
    "n": int                     # módulo RSA (n = p*q), NO es secreto
}

Formato dentro del audio:
    [ 32 bits: longitud en bits del payload JSON codificado en UTF-8 ]
    [ N bits: el payload JSON, 8 bits por byte, MSB primero          ]

Requiere que el audio sea WAV PCM (16 bits es lo más común, pero
funciona con cualquier ancho de muestra en bytes).
"""

from __future__ import annotations

import io
import json
import wave
from dataclasses import dataclass


HEADER_BITS = 32  # bits usados para guardar la longitud del payload


class CapacidadInsuficienteError(Exception):
    """El audio no tiene suficientes muestras para esconder el payload."""


class PayloadNoEncontradoError(Exception):
    """No se pudo extraer un payload válido del audio (no tiene mensaje
    escondido, o el archivo fue modificado/recomprimido y se perdió)."""


@dataclass
class InfoCapacidad:
    num_muestras: int
    bits_utilizables: int
    bits_necesarios: int

    @property
    def alcanza(self) -> bool:
        return self.bits_necesarios <= self.bits_utilizables


def _bytes_a_bits(data: bytes) -> list[int]:
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _bits_a_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8 != 0:
        bits = bits[: len(bits) - (len(bits) % 8)]
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i : i + 8]:
            byte = (byte << 1) | b
        out.append(byte)
    return bytes(out)


def _entero_a_bits(valor: int, n_bits: int) -> list[int]:
    return [(valor >> i) & 1 for i in range(n_bits - 1, -1, -1)]


def _bits_a_entero(bits: list[int]) -> int:
    valor = 0
    for b in bits:
        valor = (valor << 1) | b
    return valor


def _payload_a_dict(
    secret: list[int],
    codigos: dict,
    longitud_original: int,
    n: int,
) -> dict:
    """codigos puede venir como {simbolo: codigo} (claves int o str)."""
    simbolos = [int(k) for k in codigos.keys()]
    valores = [str(v) for v in codigos.values()]
    return {
        "secret": [int(x) for x in secret],
        "codigos_simbolos": simbolos,
        "codigos_valores": valores,
        "longitud_original": int(longitud_original),
        "n": int(n),
    }


def calcular_capacidad(audio_bytes: bytes) -> InfoCapacidad:
    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        n_frames = wf.getnframes()
        n_canales = wf.getnchannels()
        n_muestras = n_frames * n_canales
    return InfoCapacidad(num_muestras=n_muestras, bits_utilizables=n_muestras, bits_necesarios=0)


def ocultar_payload_en_wav(
    audio_bytes: bytes,
    secret: list[int],
    codigos: dict,
    longitud_original: int,
    n: int,
) -> bytes:
    """Esconde el payload (mensaje cifrado + metadatos necesarios para
    descifrarlo) dentro de un WAV, modificando el bit menos
    significativo de cada muestra PCM.

    Devuelve los bytes del nuevo WAV (mismo audio, con el mensaje
    escondido e inaudible).
    """
    payload_dict = _payload_a_dict(secret, codigos, longitud_original, n)
    payload_json = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")

    bits_payload = _bytes_a_bits(payload_json)
    bits_header = _entero_a_bits(len(bits_payload), HEADER_BITS)
    bits_totales = bits_header + bits_payload

    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        params = wf.getparams()
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    if sampwidth not in (1, 2, 3, 4):
        raise ValueError(f"Ancho de muestra no soportado: {sampwidth} bytes")

    muestras = bytearray(frames)
    n_muestras_disponibles = len(muestras) // sampwidth

    info = InfoCapacidad(
        num_muestras=n_muestras_disponibles,
        bits_utilizables=n_muestras_disponibles,
        bits_necesarios=len(bits_totales),
    )
    if not info.alcanza:
        raise CapacidadInsuficienteError(
            f"El audio solo puede esconder {info.bits_utilizables} bits, "
            f"pero el mensaje cifrado necesita {info.bits_necesarios} bits. "
            f"Usa un audio más largo o un mensaje más corto."
        )

    # El byte menos significativo de cada muestra está en la primera
    # posición si el WAV es little-endian (estándar en formato WAV).
    for i, bit in enumerate(bits_totales):
        pos = i * sampwidth  # posición del primer byte (LSB) de la muestra i
        muestras[pos] = (muestras[pos] & 0xFE) | bit

    buffer_salida = io.BytesIO()
    with wave.open(buffer_salida, "wb") as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(bytes(muestras))

    return buffer_salida.getvalue()


def extraer_payload_de_wav(audio_bytes: bytes) -> dict:
    """Extrae el payload escondido en un WAV (inverso de
    ocultar_payload_en_wav). Lanza PayloadNoEncontradoError si no
    encuentra un payload JSON válido."""
    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    muestras = bytearray(frames)
    n_muestras_disponibles = len(muestras) // sampwidth

    def leer_bits(cantidad: int, offset_muestras: int) -> list[int]:
        bits = []
        for i in range(cantidad):
            pos = (offset_muestras + i) * sampwidth
            bits.append(muestras[pos] & 1)
        return bits

    if n_muestras_disponibles < HEADER_BITS:
        raise PayloadNoEncontradoError("El audio es demasiado corto para contener un mensaje.")

    bits_header = leer_bits(HEADER_BITS, 0)
    longitud_payload_bits = _bits_a_entero(bits_header)

    if longitud_payload_bits <= 0 or (HEADER_BITS + longitud_payload_bits) > n_muestras_disponibles:
        raise PayloadNoEncontradoError(
            "No se encontró un mensaje válido en este audio (o el archivo fue "
            "recomprimido/editado y el mensaje escondido se perdió)."
        )

    bits_payload = leer_bits(longitud_payload_bits, HEADER_BITS)
    payload_json = _bits_a_bytes(bits_payload)

    try:
        payload_dict = json.loads(payload_json.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PayloadNoEncontradoError(
            "No se encontró un mensaje válido en este audio."
        ) from exc

    return payload_dict
