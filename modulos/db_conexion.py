import logging
import sqlite3
import configuracion
import datetime
from modulos.reportes_excel import ExcelReporter
import time

logging.basicConfig(level=logging.INFO)

def init_interaction_db(db_path=configuracion.INTERACTIONS_DB_PATH):
    """Inicializa la base de datos SQLite y crea la tabla de interacciones."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Creamos tabla para registrar los turnos de conversación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                speaker TEXT NOT NULL CHECK(speaker IN ('user', 'assistant')),
                text TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id ON interactions (session_id);
        ''')
        conn.commit()
        conn.close()
        logging.info(f"Base de datos de registro de interacciones inicializada en {db_path}")
    except sqlite3.Error as e:
        logging.error(f"Error al inicializar la base de datos de registro: {e}")

def export_to_excel(session_id: str, db_path=configuracion.INTERACTIONS_DB_PATH):
    """Exporta todas las interacciones de una sesión a Excel para mostras que podemos recuperar la información"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, speaker, text 
                FROM interactions 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            
            interactions = []
            current_user_input = None
            for row in cursor.fetchall():
                timestamp, speaker, text = row
                if speaker == 'user':
                    current_user_input = text
                elif speaker == 'assistant' and current_user_input:
                    interactions.append({
                        'timestamp': timestamp,
                        'user_input': current_user_input,
                        'agent_response': text,
                        'response_time': 0,  # Se calculará si existen datos de tiempo
                        'status': 'success'
                    })
                    current_user_input = None
            
            if interactions:
                reporter = ExcelReporter()
                return reporter.create_report(session_id, interactions)
    except Exception as e:
        logging.error(f"Error al exportar a Excel: {e}")
    return None

def log_interaction(session_id: str, speaker: str, text: str, db_path=configuracion.INTERACTIONS_DB_PATH, start_time=None):
    """Registra un turno de interacción (usuario o asistente) en la base de datos SQLite."""
    response_time = None
    if start_time:
        response_time = int((time.time() - start_time) * 1000)  # Convertimos a milisegundos
    
    # Implementando capacidad de almacenamiento (ahora para interacciones)
    if not session_id or not speaker or text is None: # Verificamos explícitamente si text es None para evitar errores
        logging.warning(f"Intento de registrar una interacción inválida: sesión='{session_id}', hablante='{speaker}', texto='{text}'")
        return False

    timestamp = datetime.datetime.now().isoformat()
    sql = """
        INSERT INTO interactions (session_id, timestamp, speaker, text)
        VALUES (?, ?, ?, ?);
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (session_id, timestamp, speaker, text))
            conn.commit()
            logging.info(f"Interacción registrada para la sesión {session_id}: {speaker}")
            return True
    except sqlite3.Error as e:
        logging.error(f"Error al registrar interacción en la base de datos SQLite para la sesión {session_id}: {e}")
        return False
    except Exception as e:
         logging.error(f"Error inesperado al registrar interacción: {e}")
         return False

# --- Inicializamos la base de datos cuando se carga el módulo para que se pueda usar en el resto del programa ---
init_interaction_db()
