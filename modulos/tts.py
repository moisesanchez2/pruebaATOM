from gtts import gTTS
import io
import numpy as np
import soundfile as sf
import tempfile
import os
import configuracion
import logging
from modulos.audio_manejador import audio_available, play_audio

logging.basicConfig(level=logging.INFO)

def speak_text_gtts(text, lang=configuracion.TTS_LANGUAGE):
    """Genera voz a partir de texto usando gTTS y la reproduce."""
    if not text:
        logging.warning("TTS recibió texto vacío.")
        return
        
    # Siempre imprime el texto en la consola independientemente del modo de audio
    print(f"\nAsistente IA: {text}\n")
    
    # En modo solo texto, no intentar generar o reproducir voz
    if not audio_available():
        logging.info("Ejecutando en modo solo texto, omitiendo generación de audio.")
        return
        
    logging.info(f"Generando voz para: '{text}'")
    try:
        # Generar voz con gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            temp_filename = fp.name
        
        try:
            # Convertir MP3 a formato WAV
            data, samplerate = sf.read(temp_filename)
            
            # Reproducir audio usando nuestro módulo audio_manejador
            logging.info("Reproduciendo voz generada...")
            play_audio(data, samplerate)
            logging.info("Reproducción de voz finalizada.")
        except Exception as e:
            logging.error(f"Error durante la reproducción de audio: {e}")
        finally:
            # Siempre limpiar el archivo temporal
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except Exception as e:
                logging.warning(f"No se pudo eliminar el archivo temporal: {e}")
    except Exception as e:
        logging.error(f"Error durante el procesamiento TTS: {e}")
        print(f"Error: No se pudo generar voz. Por favor, revisa los registros.")

# Exportar la función
speak = speak_text_gtts
