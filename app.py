import streamlit as st
import logging
import time
import uuid
import datetime

import configuracion
from modulos.audio_manejador import record_audio, play_audio, audio_available
from modulos.stt import transcribe_audio
from modulos.tts import speak
from modulos.agente import LeadNuturingAgent
from modulos.db_conexion import log_interaction, export_to_excel
from modulos.calendario import CalendarManager

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title=configuracion.AGENT_NAME, layout="wide")

# Determinar si el audio está disponible
modo = "Modo Audio" if audio_available() else "Modo Solo Texto"
st.title(f"{configuracion.AGENT_NAME} ({modo})")

# Inicializar sesión
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logging.info(f"Nueva sesión iniciada: {st.session_state.session_id}")

# Inicializar agente y calendario
if "agent" not in st.session_state:
    st.session_state.agent = LeadNuturingAgent()
    logging.info("LeadNuturingAgent inicializado.")

if "calendar_manager" not in st.session_state:
    st.session_state.calendar_manager = CalendarManager()
    logging.info("CalendarManager inicializado.")

# Variables de estado para la conversación
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "assistant_response" not in st.session_state:
    st.session_state.assistant_response = ""
if "show_calendar" not in st.session_state:
    st.session_state.show_calendar = False

# Disposición principal en dos columnas
col_input, col_audio = st.columns([4, 1])

with col_input:
    # Barra de texto horizontal para ingresar manualmente
    st.session_state.user_text = st.text_input("Escribe tu mensaje aquí", value="", key="text_input")
    if st.button("Enviar texto"):
        if st.session_state.user_text.strip():
            # Registrar interacción de usuario en la base de datos
            log_interaction(st.session_state.session_id, "user", st.session_state.user_text)
            # Procesar texto con el agente
            with st.spinner("Procesando texto..."):
                start_time = time.time()
                respuesta = st.session_state.agent.get_response(st.session_state.user_text)
                st.session_state.assistant_response = respuesta
                log_interaction(st.session_state.session_id, "assistant", respuesta, start_time=start_time)

                # Revisar si se menciona agendar
                if "agendar" in st.session_state.user_text.lower() or "cita" in st.session_state.user_text.lower() \
                   or "agendar" in respuesta.lower() or "cita" in respuesta.lower():
                    st.session_state.show_calendar = True

                # Reproducir respuesta si hay audio disponible
                if audio_available():
                    speak(respuesta)
                # Exportar a Excel si no se ha hecho antes
                if "exported" not in st.session_state:
                    export_to_excel(st.session_state.session_id)
                    st.session_state.exported = True

                # Limpiar texto de usuario
                st.session_state.user_text = ""

        else:
            st.warning("Por favor, ingresa un mensaje.")

with col_audio:
    if audio_available():
        # Botón para grabar audio (bloque de RECORD_SECONDS)
        if st.button("Grabar Audio"):
            st.session_state.user_text = ""
            st.session_state.assistant_response = ""
            with st.spinner("Grabando audio..."):
                audio_data, samplerate = record_audio()
            if audio_data is not None:
                st.success("Grabación completada. Transcribiendo...")
                with st.spinner("Transcribiendo..."):
                    user_input_text = transcribe_audio(audio_data, samplerate)
                if user_input_text and not user_input_text.startswith("Error:"):
                    # Guardar la transcripción como mensaje del usuario
                    st.session_state.user_text = user_input_text
                    log_interaction(st.session_state.session_id, "user", user_input_text)
                    # Procesar con el agente
                    with st.spinner("Procesando mensaje..."):
                        start_time = time.time()
                        respuesta = st.session_state.agent.get_response(user_input_text)
                        st.session_state.assistant_response = respuesta
                        log_interaction(st.session_state.session_id, "assistant", respuesta, start_time=start_time)

                        # Verificar si se menciona agendar
                        if "agendar" in user_input_text.lower() or "cita" in user_input_text.lower() \
                           or "agendar" in respuesta.lower() or "cita" in respuesta.lower():
                            st.session_state.show_calendar = True

                        if audio_available():
                            speak(respuesta)

                        if "exported" not in st.session_state:
                            export_to_excel(st.session_state.session_id)
                            st.session_state.exported = True

                        st.session_state.user_text = ""
                else:
                    st.warning("No se detectó audio o la transcripción falló.")
            else:
                st.error("Error al grabar audio.")
    else:
        st.info("No hay funcionalidad de audio disponible. Instalando 'sounddevice' y 'numpy' se habilita el modo audio.")

# Mostrar respuesta del asistente (solo la última)
if st.session_state.assistant_response:
    st.write("Respuesta del Asistente:")
    st.write(st.session_state.assistant_response)

# Sección para agendar cita
if st.session_state.show_calendar:
    st.subheader("Agendar Cita")
    col_date, col_time = st.columns(2)
    with col_date:
        meeting_date = st.date_input("Fecha", min_value=datetime.date.today())
    with col_time:
        meeting_time = st.time_input("Hora")
    
    name = st.text_input("Nombre")
    email = st.text_input("Correo electrónico")
    topic = st.text_input("Tema de la reunión")
    
    if st.button("Confirmar Cita"):
        if name and email:
            datetime_obj = datetime.datetime.combine(meeting_date, meeting_time)
            booking_result = st.session_state.calendar_manager.book_appointment(
                name, email, datetime_obj, topic
            )
            if booking_result:
                st.success(f"Cita agendada para {meeting_date} a las {meeting_time}")
                st.session_state.show_calendar = False
            else:
                st.error("No se pudo agendar la cita. Intenta otro horario.")
        else:
            st.warning("Por favor, completa nombre y correo.")
