#!/usr/bin/env python3
"""
Asistente de Nutrición de Leads ATOM - Script de Inicio Rápido
Este script verifica las dependencias necesarias e inicia la aplicación.
"""

import subprocess
import sys
import os
import importlib.util
import logging

# Configuración básica de registro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_package(package_name):
    """Verifica si un paquete de Python está instalado"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Instala un paquete de Python usando pip"""
    logging.info(f"Intentando instalar {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except Exception as e:
        logging.error(f"Error al instalar {package_name}: {e}")
        return False

def check_audio_dependencies():
    """Verifica si las dependencias relacionadas con el audio están instaladas"""
    audio_packages = ["sounddevice", "numpy", "soundfile"]
    missing = [pkg for pkg in audio_packages if not check_package(pkg)]
    
    if missing:
        logging.warning("Dependencias de audio faltantes: " + ", ".join(missing))
        logging.info("ATOM se ejecutará en modo texto sin capacidades de audio.")
        
        if input("¿Quieres instalar las dependencias de audio? (s/n): ").lower() == 's':
            for pkg in missing:
                if not install_package(pkg):
                    logging.warning(f"No se pudo instalar {pkg}. Continuando en modo texto.")
        else:
            logging.info("Continuando en modo texto.")
    else:
        logging.info("Todas las dependencias de audio están instaladas.")
    
    return len(missing) == 0

def check_core_dependencies():
    """Verifica si las dependencias principales están instaladas"""
    core_packages = ["openai", "streamlit", "langchain", "python-dotenv"]
    missing = [pkg for pkg in core_packages if not check_package(pkg)]
    
    if missing:
        logging.warning("Dependencias básicas faltantes: " + ", ".join(missing))
        if input("¿Quieres instalar las dependencias básicas? (s/n): ").lower() == 's':
            for pkg in missing:
                if not install_package(pkg):
                    logging.error(f"No se pudo instalar {pkg}. La aplicación puede fallar.")
            return True
        else:
            logging.error("Las dependencias básicas son necesarias para ejecutar la aplicación.")
            return False
    else:
        logging.info("Todas las dependencias básicas están instaladas.")
        return True

def check_api_key():
    """Verifica si la clave API de OpenAI está configurada"""
    # Primero verificar el entorno
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Luego verificar el archivo .env
    if not api_key and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if not api_key:
        logging.warning("No se encontró la clave API de OpenAI.")
        response = input("¿Quieres configurar tu clave API ahora? (s/n): ")
        if response.lower() == 's':
            api_key = input("Ingresa tu clave API de OpenAI: ")
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            logging.info("Clave API guardada en el archivo .env")
            
            # Establecerla en el entorno para esta sesión
            os.environ["OPENAI_API_KEY"] = api_key
            return True
        else:
            logging.warning("La aplicación funcionará con funcionalidad limitada sin la clave API.")
            return False
    else:
        logging.info("Clave API de OpenAI configurada.")
        return True

def start_application():
    """Iniciar la aplicación Streamlit"""
    try:
        print("\n" + "="*50)
        print("Iniciando ATOM Lead Nutrition Assistant...")
        print("="*50 + "\n")
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

def main():
    print("\n" + "="*50)
    print("Comprobación de sistema")
    print("="*50 + "\n")
    
    # Verificar primero las dependencias principales
    if not check_core_dependencies():
        print("\nLas dependencias básicas son necesarias. Por favor instálalas manualmente:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Verificar dependencias de audio
    has_audio = check_audio_dependencies()
    
    # Verificar clave API
    has_api_key = check_api_key()
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE VERIFICACIÓN:")
    print(f"Dependencias básicas: {'Instaladas' if True else 'Faltantes'}")
    print(f"Capacidades de audio: {'Instaladas' if has_audio else 'No disponibles (modo texto)'}")
    print(f"Clave API de OpenAI: {'Configurada' if has_api_key else 'No configurada (limitado)'}")
    print("="*50 + "\n")
    
    # Iniciar aplicación
    start_application()

if __name__ == "__main__":
    main() 