import pytest
from playwright.sync_api import expect
from pages.assistant_page import AssistantPage
import pytest

pytestmark = pytest.mark.e2e
def test_assistant_generates_architecture(page):

    assistant = AssistantPage(page)

    # ==========================================
    # ASI-001 / ASI-002
    # Consulta y generación de arquitectura
    # ==========================================

    assistant.open_assistant()

    expect(assistant.query_input).to_be_visible()
    expect(assistant.conversation).to_be_visible()

    query = (
        "Necesito una tienda B2B de logística que gestione "
        "cuentas empresariales, pagos, inventario y rutas de reparto."
    )

    assistant.write_query(query)

    # Verificar que el botón esté habilitado
    expect(assistant.send_button).to_be_enabled(timeout=15000)

    # Capturar la respuesta HTTP durante el envío
    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and "/api/v1/assistant/chat" in response.url
        ),
        timeout=90000
    ) as response_info:

        assistant.send_button.click()

    response = response_info.value

    # Clasificar indisponibilidad temporal
    if response.status in (502, 503, 504):
        pytest.skip(
            f"DEPENDENCIA NO DISPONIBLE: HTTP {response.status}. "
            "El asistente no pudo procesar la consulta."
        )

    # Detectar otros errores HTTP
    assert response.status == 200, (
        f"Error HTTP del asistente: {response.status}. "
        f"Respuesta: {response.text()[:500]}"
    )

    # Esperar a que termine la generación
    assistant.wait_for_response()

    # Obtener contenido de la conversación
    conversation_text = assistant.get_conversation_text()

    # Validar consulta enviada
    assert query in conversation_text

    # ==========================================
    # ASI-002
    # Validar contenido de la propuesta
    # ==========================================

    expect(assistant.conversation).to_contain_text(
        "Stack recomendado"
    )

    expect(assistant.conversation).to_contain_text(
        "Mapa de arquitectura"
    )

    expect(assistant.conversation).to_contain_text(
        "Cómo se conectan"
    )

    expect(assistant.conversation).to_contain_text(
        "Fuentes del catálogo"
    )

    # Validar descarga de propuesta
    expect(
        assistant.conversation.get_by_text(
            "Descargar propuesta (.zip)"
        )
    ).to_be_visible()

    # ==========================================
    # ASI-003.1
    # Persistencia de conversación
    # ==========================================

    assistant.reload_assistant()

    expect(
        assistant.previous_conversation_notice
    ).to_be_visible()

    expect(
        assistant.previous_conversation_notice
    ).to_contain_text(
        "Continuamos tu conversación anterior."
    )

    expect(
        assistant.conversation
    ).to_contain_text(query)

    # ==========================================
    # ASI-003.2 / ASI-003.3
    # Nueva conversación y campo disponible
    # ==========================================

    expect(
        assistant.recovered_new_conversation_button
    ).to_be_enabled()

    assistant.start_new_conversation_from_notice()

    expect(
        assistant.previous_conversation_notice
    ).to_be_hidden()

    expect(
        assistant.conversation
    ).not_to_contain_text(query)

    expect(assistant.query_input).to_be_visible()
    expect(assistant.query_input).to_have_value("")
    expect(assistant.query_input).to_be_enabled()
