import os
from dotenv import load_dotenv

# para que funcione con pydantic v1 en langchain

# cargamos las variables de entorno del .env
load_dotenv()

#Apikey de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# modelo para la conversación
LLM_MODEL_NAME = "gpt-3.5-turbo"

# modelo para reconocimiento de voz (ASR)
WHISPER_MODEL_NAME = "whisper-1"

# frecuencia de muestreo para grabar audio (16kHz funciona bien para voz)
AUDIO_SAMPLE_RATE = 16000  # Hz

# número de canales de audio (1 = mono, recomendado para reconocimiento de voz)
AUDIO_CHANNELS = 1

# duración máxima de grabación por cada intervención del usuario para pruebas rápidas
RECORD_SECONDS = 12  # segundos

# código de idioma para el motor TTS 
TTS_LANGUAGE = 'es'

# ruta al archivo SQLite para guardar historial de conversación
INTERACTIONS_DB_PATH = "interaction_log.db"

# ruta para los archivos Excel exportados
EXCEL_EXPORT_PATH = "interaction_exports/"

# nombre visible del asistente
AGENT_NAME = "Lead Nutrition Assistant"

# control de creatividad en las respuestas del modelo
LLM_TEMPERATURE = 0.7

# máximo de intentos para aclarar lo que dijo el usuario si no se entiende
MAX_CLARIFICATION_ATTEMPTS = 2

# duración por defecto de una cita en minutos
DEFAULT_APPOINTMENT_DURATION = 60

# endpoint de la API del CRM si desearamos integrar uno real
CRM_API_ENDPOINT = os.getenv("CRM_API_ENDPOINT", None)

# clave API para autenticarse con el CRM
CRM_API_KEY = os.getenv("CRM_API_KEY", None)

# ----------------------------------------------------
# Validación
# ----------------------------------------------------
if not OPENAI_API_KEY:
    print("AVISO: No se encontró OPENAI_API_KEY en las variables de entorno.")
    print("La aplicación funcionará con funciones limitadas.")
    print("Configura tu clave en un archivo .env o como variable de entorno.")

# validación opcional para el CRM (descomentar si se implementa)
# if not CRM_API_ENDPOINT or not CRM_API_KEY:
#     print("AVISO: No se encontraron las credenciales del CRM (CRM_API_ENDPOINT, CRM_API_KEY).")
#     print("La integración con el CRM estará deshabilitada.")
