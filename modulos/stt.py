import openai
import configuracion
import io
import numpy as np
import wave
import logging
from modulos.audio_manejador import audio_available
import time

logging.basicConfig(level=logging.INFO)

def transcribe_audio(audio_data, samplerate):
    """Transcribe datos de audio utilizando el modelo Whisper de OpenAI."""
    logging.info("Transcribiendo audio...")
    
    # Manejar modo solo texto
    if not audio_available():
        logging.info("Ejecutando en modo solo texto. Solicitando entrada de texto en lugar de audio.")
        try:
            user_input = input("Por favor, escribe tu mensaje (modo solo texto): ")
            logging.info(f"Texto recibido: {user_input}")
            return user_input
        except Exception as e:
            logging.error(f"Error al obtener entrada de texto: {e}")
            return "Ocurrió un error en modo solo texto."
    
    # Manejar transcripción de audio normal para interacciones reales
    if audio_data is None:
        logging.error("No se recibieron datos de audio para transcripción.")
        return None
        
    try:
        # Verificar clave API
        if not configuracion.OPENAI_API_KEY:
            logging.error("No se encontró clave API de OpenAI. Por favor, configura tu clave API en configuracion.py")
            return "Error: Clave API de OpenAI no configurada."
            
        # Establecer clave API
        openai.api_key = configuracion.OPENAI_API_KEY
        
        # Convertir audio a WAV para que OpenAI pueda procesarlo correctamente
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(configuracion.AUDIO_CHANNELS)
            wf.setsampwidth(audio_data.dtype.itemsize)
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
        buffer.seek(0)
        buffer.name = "input.wav"

        # Transcribir con OpenAI
        transcript = openai.audio.transcriptions.create(
            model=configuracion.WHISPER_MODEL_NAME,
            file=buffer,
            language="es"
        )
        
        if hasattr(transcript, 'text') and transcript.text:
            logging.info(f"Transcripción exitosa: {transcript.text}")
            return transcript.text
        else:
            logging.warning("Se recibió una transcripción vacía de OpenAI")
            return "No se detectó texto en el audio."
            
    except openai.APIError as e:
        logging.error(f"Error de API de OpenAI durante la transcripción: {e}")
        return f"Error: No se pudo transcribir el audio. {e}"
    except openai.APIConnectionError as e:
        logging.error(f"Error de conexión con API de OpenAI: {e}")
        return "Error: No se pudo conectar a la API de OpenAI. Por favor, verifica tu conexión a internet."
    except openai.RateLimitError as e:
        logging.error(f"Límite de tasa de OpenAI excedido: {e}")
        return "Error: Límite de tasa de OpenAI excedido. Por favor, intenta más tarde."
    except Exception as e:
        logging.error(f"Error inesperado durante la transcripción: {e}")
        return "Error: No se pudo transcribir el audio debido a un problema inesperado."
