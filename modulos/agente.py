import logging
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import configuracion
import prompts.prompt_general as system_prompts
import os

logging.basicConfig(level=logging.INFO)

class LeadNuturingAgent:
    def __init__(self):
        """Inicializa el Agente de Nutrición de Leads."""
        if not configuracion.OPENAI_API_KEY:
            logging.warning("¡No se encontró la API key de OpenAI! Por favor configúrala en configuracion.py")
            print("\n" + "="*50)
            print("ADVERTENCIA: NO SE ENCONTRÓ LA API KEY DE OPENAI")
            print("="*50 + "\n")
            print("Por favor configura tu API key en configuracion.py")
            print("Puedes obtener una API key en: https://platform.openai.com/api-keys")
            print("\n" + "="*50 + "\n")
        
        try:
            # Usamos el modelo GPT-3.5 Turbo 
            self.llm = ChatOpenAI(
                temperature=configuracion.LLM_TEMPERATURE, 
                model_name=configuracion.LLM_MODEL_NAME, 
                api_key=configuracion.OPENAI_API_KEY
            )

            # Definimos la estructura del prompt
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompts.BASE_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ])

            # Configuración de Langchain para la memoria de conversación
            self.memory = ConversationBufferMemory(return_messages=True, memory_key="history")

            self.conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
                memory=self.memory
            )
            self.clarification_attempts = 0
            
            # Mensaje de éxito
            logging.info("Agente de Nutrición de Leads inicializado correctamente")
            
        except Exception as e:
            logging.error(f"Error al inicializar el Agente de Nutrición de Leads: {e}")
            print(f"\n ERROR DE INICIALIZACIÓN: {e}\n")

    def get_response(self, user_input):
        """Obtiene respuesta del LLM basada en la entrada del usuario y el historial de conversación."""
        if not user_input or user_input.strip() == "":
            return "No se ha detectado ninguna entrada. Por favor, intenta de nuevo."
            
        logging.info(f"Enviando al LLM: {user_input}")
        
        # Imprimimos la entrada del usuario con formato
        print("\n" + "="*80)
        print(f"USUARIO: {user_input}")
        print("="*80 + "\n")
        
        try:
            if not configuracion.OPENAI_API_KEY:
                raise ValueError("API key de OpenAI no configurada")
                
            # Mostramos estado de procesamiento
            print("Procesando solicitud...")

            # Obtenemos la respuesta del modelo
            llm_result = self.conversation.invoke({"input": user_input})
            if hasattr(llm_result, 'content'):
                response = llm_result.content
            elif isinstance(llm_result, dict):
                response = llm_result.get("text", "")
            else:
                response = str(llm_result)
            
            # Mejoramos la visibilidad en consola con formato claro
            print("\n" + "="*80)
            print("ATOM RESPUESTA:")
            print("="*80)
            print(f"\n{response}\n")
            print("="*80 + "\n")
            
            logging.info(f"Respuesta del LLM: {response}") 
            self.clarification_attempts = 0 # Reiniciamos al obtener respuesta exitosa
            return response
            
        except ValueError as e:
            logging.error(f"Error de configuración: {e}")
            print(f"\n ERROR DE CONFIGURACIÓN: {e}\n")
            return f"Error de configuración: {e}. Por favor, verifica tu configuración de API."
            
        except Exception as e:
            logging.error(f"Error durante la interacción con el LLM: {e}")
            print("\n" + "="*80)
            print(f"ERROR: {e}")
            print("="*80 + "\n")
            
            # Manejo de errores
            if self.clarification_attempts < configuracion.MAX_CLARIFICATION_ATTEMPTS:
                self.clarification_attempts += 1
                logging.warning("Intentando clarificación...")
                return system_prompts.INTENT_CLARIFICATION_PROMPT
            else:
                logging.error("Se alcanzó el máximo de intentos de clarificación.")
                return "Lo siento, estoy teniendo problemas para procesar tu solicitud en este momento. Por favor, intenta de nuevo más tarde."

