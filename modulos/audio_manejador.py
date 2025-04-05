# Intentamos importar sounddevice, pero proporcionamos alternativa
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    logging.warning("El módulo sounddevice no está instalado. Ejecutando en modo solo texto.")
    AUDIO_AVAILABLE = False

import logging
import numpy as np
import queue
import configuracion
import time

logging.basicConfig(level=logging.INFO)

audio_queue = queue.Queue()

def record_audio(duration=configuracion.RECORD_SECONDS, samplerate=configuracion.AUDIO_SAMPLE_RATE, channels=configuracion.AUDIO_CHANNELS):
    """Graba audio desde el micrófono durante un tiempo especificado para regular interacciones en las pruebas."""
    
    # Verificamos si la funcionalidad de audio está disponible
    if not AUDIO_AVAILABLE:
        logging.warning("La grabación de audio no está disponible en modo solo texto.")
        return None, None
    
    logging.info(f"Grabando durante {duration} segundos...")
    try:
        # Intentamos obtener la información del dispositivo predeterminado
        try:
            device_info = sd.query_devices(None, 'input')
            logging.info(f"Usando dispositivo de audio: {device_info['name']}")
        except Exception as e:
            logging.warning(f"No se pudo consultar el dispositivo de audio: {e}")
        
        # Grabamos audio
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
        sd.wait()
        logging.info("Grabación finalizada.")
        
        # Verificamos si la grabación contiene datos válidos
        if recording.size == 0 or np.all(recording == 0):
            logging.warning("La grabación parece estar vacía o en silencio.")
            return None, None
            
        return recording, samplerate
    except Exception as e:
        logging.error(f"Error durante la grabación de audio: {e}")
        return None, None

def play_audio(audio_data, samplerate=configuracion.AUDIO_SAMPLE_RATE):
    """Reproduce datos de audio usando el dispositivo de sonido predeterminado."""
    
    # Verificamos si la funcionalidad de audio está disponible
    if not AUDIO_AVAILABLE:
        logging.warning("La reproducción de audio no está disponible en modo solo texto.")
        return
    
    if audio_data is None:
        logging.warning("No se proporcionaron datos de audio para reproducir.")
        return
        
    logging.info("Reproduciendo respuesta de audio...")
    try:
        # Intentamos obtener la información del dispositivo predeterminado
        try:
            device_info = sd.query_devices(None, 'output')
            logging.info(f"Usando dispositivo de audio: {device_info['name']}")
        except Exception as e:
            logging.warning(f"No se pudo consultar el dispositivo de audio: {e}")
            
        # Reproducimos audio
        sd.play(audio_data, samplerate)
        sd.wait()
        logging.info("Reproducción finalizada.")
    except Exception as e:
        logging.error(f"Error al reproducir audio: {e}")

def audio_available():
    """Devuelve si la grabación/reproducción de audio está disponible"""
    return AUDIO_AVAILABLE
