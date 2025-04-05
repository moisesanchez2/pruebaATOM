import logging
import datetime
import json
import os

class CalendarManager:
    """Clase para gestionar citas de calendario y funcionalidad de programación"""
    
    def __init__(self):
        """Inicializa el gestor de calendario con un almacenamiento simple en JSON"""
        self.appointments_file = "calendario_citas.json"
        self.appointments = self._load_appointments()
        logging.info("Gestor de Calendario inicializado")
    
    def _load_appointments(self):
        """Carga las citas desde un archivo JSON o lo crea si no existe"""
        if os.path.exists(self.appointments_file):
            try:
                with open(self.appointments_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logging.error(f"Error al cargar las citas: {e}")
                return {"appointments": []}
        else:
            return {"appointments": []}
    
    def _save_appointments(self):
        """Guarda las citas en un archivo JSON"""
        try:
            with open(self.appointments_file, 'w') as file:
                json.dump(self.appointments, file, indent=4, default=str)
            return True
        except Exception as e:
            logging.error(f"Error al guardar las citas: {e}")
            return False
    
    def book_appointment(self, name, email, datetime_obj, topic="Consulta general"):
        """Reserva una nueva cita
        
        Args:
            name (str): Nombre del cliente
            email (str): Correo electrónico del cliente
            datetime_obj (datetime): Fecha y hora de la cita
            topic (str): Tema de la reunión
            
        Returns:
            bool: Éxito o fracaso
        """
        # Detección simple de colisiones (no permitir citas en la misma hora)
        hour_start = datetime_obj.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + datetime.timedelta(hours=1)
        
        # Comprobar si existen citas en el mismo intervalo de tiempo
        for appointment in self.appointments["appointments"]:
            appt_time = None
            if isinstance(appointment["datetime"], str):
                try:
                    appt_time = datetime.datetime.fromisoformat(appointment["datetime"])
                except ValueError:
                    # Intentar analizar el formato de cadena
                    appt_time = datetime.datetime.strptime(appointment["datetime"], "%Y-%m-%d %H:%M:%S")
            else:
                appt_time = appointment["datetime"]
                
            if appt_time and hour_start <= appt_time < hour_end:
                logging.warning(f"Se detectó una colisión de citas en {hour_start}")
                return False
        
        # Crear nueva cita
        new_appointment = {
            "id": len(self.appointments["appointments"]) + 1,
            "name": name,
            "email": email,
            "datetime": datetime_obj,
            "topic": topic,
            "created_at": datetime.datetime.now()
        }
        
        # Añadir a la lista y guardar
        self.appointments["appointments"].append(new_appointment)
        success = self._save_appointments()
        if success:
            logging.info(f"Cita reservada para {name} el {datetime_obj}")
        return success
    
    def get_appointments(self, email=None):
        """Obtiene todas las citas o filtra por correo electrónico
        
        Args:
            email (str, opcional): Filtrar por correo electrónico del cliente
            
        Returns:
            list: Lista de citas
        """
        if not email:
            return self.appointments["appointments"]
        
        return [a for a in self.appointments["appointments"] 
                if a["email"].lower() == email.lower()]
    
    def cancel_appointment(self, appointment_id):
        """Cancela una cita por ID
        
        Args:
            appointment_id (int): El ID de la cita a cancelar
            
        Returns:
            bool: Éxito o fracaso
        """
        original_length = len(self.appointments["appointments"])
        self.appointments["appointments"] = [
            a for a in self.appointments["appointments"] if a["id"] != appointment_id
        ]
        
        if len(self.appointments["appointments"]) < original_length:
            success = self._save_appointments()
            if success:
                logging.info(f"Cita {appointment_id} cancelada")
            return success
        return False 