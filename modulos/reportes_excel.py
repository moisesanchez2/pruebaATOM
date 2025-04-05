import openpyxl
from datetime import datetime
import os
import configuracion

class ExcelReporter:
    def __init__(self):
        self.report_dir = "reportes_interacciones"
        os.makedirs(self.report_dir, exist_ok=True)
        
    def create_report(self, session_id, interactions):
        """Crea un informe en Excel con todas las interacciones a falta de CRM real o DB real"""
        filename = f"{self.report_dir}/interacciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Interacciones"
        
        # Encabezados
        headers = [
            "Fecha/Hora", "Sesión ID", "Usuario", 
            "Asistente", "Tiempo Respuesta (ms)", "Estado"
        ]
        ws.append(headers)
        
        # Filas de datos
        for interaction in interactions:
            ws.append([
                interaction["timestamp"],
                session_id,
                interaction["user_input"],
                interaction["agent_response"],
                interaction["response_time"],
                interaction["status"]
            ])
        
        wb.save(filename)
        return filename
