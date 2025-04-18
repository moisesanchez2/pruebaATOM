# ATOM - Lead Assistant

Este proyecto es parte de la prueba técnica de Carlos Moisés Méndez para un ejercicio para Atom en la posición como Ingeniero de AI. 

Es un asistente virtual que conversa con posibles clientes para ayudar a manejar sus interacciones iniciales, dar información básica y agendar citas. Por ahora, como no tenemos acceso a un CRM real, simplemente guardamos las conversaciones en un archivo Excel. Si en el futuro se quisiera conectar a un CRM, solo habría que modificar la configuración y apuntar a la API correcta.

## Lo que hace

- Habla y escucha si tienes micrófono y bocinas (modo audio)
- Funciona solo con texto si no tienes audio
- Permite agendar citas con un calendario simple
- Guarda todas las conversaciones 
- Da respuestas inteligentes usando OpenAI GPT (podríamos incluir otros modelos a traves de las apis propias u open router dependiendo de la necesidad)

## Lo que necesitas

- Python 3.9 o más reciente
- Una clave API de OpenAI (para que el asistente pueda pensar y entender voz)

## Cómo instalarlo

1. Descarga el código:
```bash
git clone https://github.com/tu-usuario/atom-assistant.git
cd atom-assistant
```

2. Instala lo que necesita:
```bash
pip install -r requirements.txt
```

3. Configura tu clave de OpenAI:
   - Crea un archivo `.env` en la carpeta principal como referencia de
   - Escribe esto: `OPENAI_API_KEY=tu-clave-api`

## Cómo funciona

### Con audio (si tienes micrófono)
Puedes hablarle al asistente y te responderá con voz.

#### Para que funcione con audio necesitas:
- Tener instalado `sounddevice`
- Un micrófono y bocinas que funcionen

### Solo texto (automático si no hay audio)
Si no tienes micrófono o faltan los módulos de audio, funcionará solo con texto:
- Todo se hace escribiendo y leyendo
- No necesitas equipo de audio
- Hace todo lo mismo excepto hablar y escuchar

## Cómo usarlo

1. Inicia la aplicación:
```bash
streamlit run app.py
```

2. Platica con el asistente:
   - Si tienes audio: Usa el botón para grabar tu voz (puedes modificar cuántos segundos máximo puedes hablar por interacción en el archivo configuración.py, default son 12)
   - Si no: Escribe en el cuadro de texto

3. Puedes para este ejercicio:
   - Preguntar sobre servicios de nutrición
   - Pedir información de planes
   - Agendar citas con nutriólogos

## Problemas comunes 

### "No module named 'sounddevice'"
No te preocupes, funcionará solo con texto. Si quieres usar audio:
```bash
pip install sounddevice numpy
```

### Problemas con la API de OpenAI
Revisa que tu clave esté bien escrita en el archivo `.env` o en `configuracion.py`.

## Cómo está organizado

- `app.py`: La aplicación principal con la interfaz para cargarlo
- `modulos/`: Las partes que hacen todo el trabajo del back
  - `audio_manejador.py`: Maneja la grabación y reproducción de audio
  - `stt.py`: Convierte voz a texto 
  - `tts.py`: Convierte texto a voz 
  - `agente.py`: El cerebro del asistente para su interaccion
  - `calendario.py`: Para agendar citas si se deseara
  - `db_conexion.py`: Guarda las conversaciones en archivo db
- `prompts/`: Instrucciones para el asistente detallando lo esperado de él
- `configuracion.py`: Ajustes del sistema para escalar
- `requirements.txt`: Lo que necesita instalar para que funcione
