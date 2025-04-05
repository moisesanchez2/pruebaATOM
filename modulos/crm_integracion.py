import logging
import requests  # para hacer las llamadas a la API
from typing import Dict, Optional, Any
import configuracion  # para traer la configuración

logging.basicConfig(level=logging.INFO)

class CRMClient:
    """
    Cliente para comunicarse con la API del CRM.
    Maneja la autenticación y tiene métodos para gestionar los leads.
    """
    def __init__(self):
        """
        Inicia el cliente CRM, carga la configuración y prepara la autenticación.
        """
        self.api_endpoint = configuracion.CRM_API_ENDPOINT
        self.api_key = configuracion.CRM_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_endpoint or not self.api_key:
            logging.warning("Endpoint o key del CRM no configurados. La integración CRM se deshabilita.")
            self.enabled = False
        else:
            self.enabled = True
            logging.info(f"Cliente CRM iniciado para endpoint: {self.api_endpoint}")

    def _make_request(self, method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Método auxiliar para hacer peticiones a la API del CRM.
        Verifica errores básicos.
        """
        if not self.enabled:
            logging.warning("Se intentó realizar una petición al CRM pero el cliente está deshabilitado.")
            return None
            
        url = f"{self.api_endpoint}/{path.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()  # Lanza HTTPError si la respuesta es mala (4xx o 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Falló la petición a la API del CRM: {e}")
            return None
        except Exception as e:
            logging.error(f"Ocurrió un error inesperado durante la petición al CRM: {e}")
            return None

    def get_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del lead del CRM usando el email.
        
        Args:
            email: El email del lead a buscar.
            
        Returns:
            Un diccionario con datos del lead si se encuentra, si no None.
        """
        if not email:
            logging.warning("Se intentó obtener lead con email vacío.")
            return None
            
        logging.info(f"Intentando obtener lead con email: {email}")
        # Ruta de ejemplo, ajustar según la API del CRM real
        path = f"leads?email={email}" 
        response_data = self._make_request("GET", path)
        
        # Asumiendo que la API regresa una lista, posiblemente vacía
        if response_data and isinstance(response_data, list) and len(response_data) > 0:
            logging.info(f"Lead encontrado para email {email}.")
            return response_data[0] # Regresamos el primer match
        elif response_data is not None:
             logging.info(f"No se encontró lead para email {email}.")
             return None
        else:
             # Ocurrió error durante la petición
             return None

    def update_or_create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza un lead existente o crea uno nuevo en el CRM.
        Necesita al menos el campo 'email' en lead_data.
        
        Args:
            lead_data: Un diccionario con la info del lead (ej. nombre, email, empresa, necesidades).
            
        Returns:
            Un diccionario con los datos del lead actualizado/creado del CRM, o None si falló.
        """
        if not self.enabled:
            return None
            
        email = lead_data.get("email")
        if not email:
            logging.error("No se puede actualizar/crear lead sin email.")
            return None

        logging.info(f"Intentando actualizar o crear lead para email: {email}")
        
        # 1. Verificamos si el lead existe
        existing_lead = self.get_lead_by_email(email)
        
        if existing_lead:
            # 2a. Actualizamos lead existente
            lead_id = existing_lead.get("id") # Asumiendo que el CRM da un 'id'
            if not lead_id:
                 logging.error(f"No se pudo obtener ID para lead existente con email {email}.")
                 return None
            logging.info(f"Actualizando lead existente (ID: {lead_id}) para email: {email}")
            path = f"leads/{lead_id}"
            # ¿Mezclar datos o solo mandar los nuevos? Depende de la API. Asumimos que mandar todo actualiza.
            response_data = self._make_request("PUT", path, json=lead_data) 
        else:
            # 2b. Creamos lead nuevo
            logging.info(f"Creando nuevo lead para email: {email}")
            path = "leads"
            response_data = self._make_request("POST", path, json=lead_data)
            
        if response_data:
            logging.info(f"Lead actualizado/creado con éxito para {email}.")
            return response_data
        else:
            logging.error(f"Falló al actualizar/crear lead para {email}.")
            return None
