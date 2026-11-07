import logging
import asyncio
import random

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMService:

    DEFAULT_MODEL = "gemini-3.1-flash-lite"
    FALLBACK_MODEL = "gemini-3.5-flash-lite"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.5

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.3,
        max_output_tokens: int = 8192,
    ):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        if not model:
            raise ValueError("Model cannot be empty")

        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

        if max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    async def _generate(
        self,
        context: str,
        json_mode: bool = False,
    ) -> str:

        if not context or not context.strip():
            raise ValueError("Context cannot be empty")

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

        models = [self.model, self.FALLBACK_MODEL]

        for model_index, model in enumerate(models):
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    response = await self.client.aio.models.generate_content(
                        model=model,
                        contents=context,
                        config=config,
                    )

                    content = response.text

                    if not content:
                        raise RuntimeError("Gemini returned an empty response")

                    logger.info(
                        "Response generated successfully using Gemini model %s",
                        model,
                    )

                    return content.strip()

                except Exception as exc:
                    error_message = str(exc).upper()

                    retryable = any(
                        indicator in error_message
                        for indicator in (
                            "503",
                            "429",
                            "UNAVAILABLE",
                            "RESOURCE_EXHAUSTED",
                        )
                    )

                    if not retryable:
                        logger.exception(
                            "Gemini generation failed | model=%s",
                            model,
                        )
                        raise

                    if attempt == self.MAX_RETRIES:
                        if model_index == len(models) - 1:
                            logger.exception(
                                "All Gemini models exhausted | model=%s",
                                model,
                            )
                            raise

                        logger.warning(
                            "Model %s exhausted retries. Switching to fallback: %s",
                            model,
                            self.FALLBACK_MODEL,
                        )
                        break

                    delay = self.RETRY_DELAY + random.uniform(0, 0.5)

                    logger.warning(
                        "Gemini temporarily unavailable | model=%s | "
                        "retry in %.2f seconds | attempt %s/%s",
                        model,
                        delay,
                        attempt + 1,
                        self.MAX_RETRIES,
                    )

                    await asyncio.sleep(delay)

    async def generate_architecture(self, context: str) -> str:
        prompt = f"""
    {context}

    Tu tarea es proponer una arquitectura técnica estructurada.

    Devolvé exclusivamente JSON válido con esta estructura:

    {{
        "components": [
            {{
                "key": "identificador_unico",
                "repository_id": 102,
                "full_name": "owner/repository",
                "role": "Responsabilidad dentro de la arquitectura",
                "license": "Apache-2.0",
                "health_status": "Activo",
                "justification": "Justificación basada en la evidencia"
            }}
        ],
        "connections": [
            {{
                "from": "componente_origen",
                "to": "componente_destino",
                "label": "Descripción de la conexión",
                "verified": false,
                "integration_code": null
            }}
        ],
        "suggested_questions": [
            "Pregunta de seguimiento"
        ]
    }}

    Reglas:
    - Utilizá únicamente repositorios presentes en el contexto.
    - Seleccioná los repositorios que cubran las funcionalidades detectadas en los requisitos.
    - Incluí componentes especializados cuando cubran funcionalidades solicitadas, aunque no sean parte del núcleo de la solución.
    - Si hay un repositorio disponible para autenticación o gestión de identidad y el usuario solicita autenticación, consideralo como componente de la arquitectura.
    - Si hay un repositorio disponible para pagos y el usuario solicita gestión de pagos, consideralo como componente de la arquitectura.
    - Aplicá el mismo criterio a notificaciones, logística y demás funcionalidades solicitadas.
    - Cuando el usuario solicite logística, transporte o gestión de flota,
      incluí los repositorios especializados disponibles para esas funciones.
    - Si Project-OSRM/osrm-backend está disponible en el contexto y se solicitan
      logística o envíos, incluilo como componente de planificación y cálculo de rutas.
    - Si traccar/traccar está disponible y se solicita seguimiento de vehículos
      o logística, incluilo como componente de seguimiento de flota.
    - No sustituyas un componente especializado por otro que cubra una función diferente.
    - Si existen repositorios especializados para esas funcionalidades,
      incluilos como componentes independientes de la arquitectura,
      aunque la plataforma principal de e-commerce no las implemente.
    - Si el usuario solicita gestión de pagos y existe un repositorio
      especializado en pagos dentro del contexto, incluilo obligatoriamente
      como componente independiente de la arquitectura.
    - Proponé conexiones entre la plataforma principal y los componentes
      especializados cuando tengan sentido funcional.
    - Cuando incluyas OSRM en una arquitectura de e-commerce con logística,
      proponé una conexión desde la plataforma principal hacia OSRM
      para consultar y calcular rutas de entrega.
    - Cuando incluyas Traccar en esa arquitectura, proponé una conexión
      desde la plataforma principal hacia Traccar para transmitir datos
      de despacho y asociar pedidos con el seguimiento de vehículos.
    - Estas conexiones representan integraciones personalizadas:
      utilizá verified=false e integration_code=null si no existe
      evidencia explícita de una integración implementada.
    - No asumas que OSRM y Traccar necesitan una conexión directa entre sí.
    - No inventes conectores, APIs ni integraciones implementadas.
    - No incluyas repositorios que no aporten directamente a los requisitos.
    - No inventes IDs, licencias ni estados de mantenimiento.
    - No inventes integraciones ni códigos.
    - Una conexión solo puede tener verified=true si existe evidencia explícita.
    - Generá entre 2 y 3 preguntas sugeridas.
    - Las preguntas deben ser consultas técnicas que el usuario pueda
      realizar para profundizar en la arquitectura propuesta.
    - Deben referirse a componentes, integraciones o implementaciones
      concretas de los repositorios seleccionados.
    - No hagas preguntas para recopilar requisitos, preferencias,
      presupuestos, volúmenes de uso ni información del negocio.
    - Ejemplos:
      "¿Cómo conecto Vendure con Hyperswitch para procesar pagos?"
      "¿Cómo integro Novu para enviar notificaciones de pedidos?"
      "¿Cómo puedo combinar OSRM y Traccar para gestionar los envíos?"
    - Si no hay evidencia suficiente para una arquitectura, devolvé componentes y conexiones vacíos.
    - Si devolvés componentes vacíos, las preguntas sugeridas deben invitar a
      reformular la necesidad dentro del catálogo de OpenBridge, nunca a buscar
      software fuera de él.
    - No incluyas Markdown ni explicaciones fuera del JSON.
    - repository_id, full_name, license y health_status deben corresponder exactamente a los datos del contexto.
    - No inventes ni modifiques esos valores.
    - Si un dato no está disponible, utilizá null cuando el campo lo permita.
    """

        return await self.generate_json_response(prompt)

    async def generate_response(self, context: str) -> str:

        prompt = f"""
        {context}

        Tu tarea es responder la consulta del usuario y recomendar
        repositorios open source adecuados para sus requisitos.

        Reglas:
        - Utilizá exclusivamente repositorios incluidos en
          CATÁLOGO PARA RECOMENDAR.
        - Podés presentar alternativas cuando existan varias opciones válidas.
        - Diferenciá claramente entre la plataforma principal y los componentes
          especializados que complementan su funcionalidad.
        - Cuando presentes varias alternativas para una misma función,
          explicá sus diferencias y criterios de elección.
        - Mantené coherencia con la arquitectura propuesta: si se selecciona
          una alternativa como componente principal, explicá por qué resulta
          adecuada frente a las demás alternativas mencionadas.
        - No presentes como seleccionados componentes que no estén disponibles
          en el contexto.
        - No inventes repositorios, funcionalidades, integraciones ni códigos.
        - Diferenciá las integraciones documentadas de aquellas que requieren
          desarrollo personalizado.
        - No afirmes que una integración está implementada si no existe
          evidencia explícita.
        - Cuando menciones limitaciones, explicalas en términos concretos
          y comprensibles para el usuario.
        - Evitá expresiones internas como "repositorios autorizados",
          "información proporcionada" o "evidencia disponible".
        - No afirmes que una solución cubre funcionalidades que no implementa.
        - No incluyas preguntas de seguimiento en esta respuesta.
        - Si se genera una arquitectura, utilizá sus componentes para explicar
          la solución finalmente seleccionada.
        - Si la arquitectura selecciona una de varias alternativas para una función,
          identificá explícitamente esa alternativa como la elegida y explicá por qué.
        - Podés mencionar otras alternativas, pero diferenciá claramente
          entre alternativas evaluadas y componentes seleccionados.
        - No menciones repositorios que no estén incluidos en
          CATÁLOGO PARA RECOMENDAR o que no estén disponibles
          en el contexto de integraciones.
        - Cuando la arquitectura incluya OSRM y Traccar, explicá sus funciones
          por separado: OSRM para cálculo de rutas y Traccar para seguimiento
          de vehículos.
        - No atribuyas a un repositorio funcionalidades de otro.
        - Evitá expresiones que hagan referencia al contexto interno del sistema,
          como "la información disponible", "la información proporcionada",
          "los repositorios autorizados", "la lista proporcionada",
          "los repositorios analizados", "la arquitectura técnica validada",
          "el stack seleccionado", "el contexto" o "la evidencia proporcionada".
          Hablá directamente del catálogo de OpenBridge o de las herramientas recomendadas.
        - Si la consulta es muy general y no describe funcionalidades concretas
          (por ejemplo, "quiero una app para mi negocio"), empezá con una frase
          que diga qué tipo de negocio supusiste y cerrá invitando al usuario
          a describir su negocio (qué vende u ofrece, a quién y qué procesos
          quiere resolver) para ajustar la propuesta.
        - Si ninguna herramienta del catálogo cubre la necesidad, decilo con
          claridad y sin inventar alternativas fuera del catálogo.
        - Cuando recomiendes un repositorio con licencia GPL-3.0,
          explicá brevemente sus implicaciones:
          las obligaciones de distribuir el código fuente correspondiente
          pueden aplicar cuando se distribuyen versiones modificadas
          u obras derivadas cubiertas por la licencia.
          Aclará que el uso interno sin distribución no obliga por sí solo
          a publicar el código fuente.
          No afirmes que cualquier uso obliga a liberar toda la solución.

        Respondé en español, con una explicación técnica clara y estructurada.
        """

        return await self._generate(prompt)

    async def generate_json_response(self, context: str) -> str:
        return await self._generate(context, json_mode=True)
