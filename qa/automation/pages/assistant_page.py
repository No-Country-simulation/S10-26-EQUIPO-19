from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class AssistantPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        self.query_input = page.locator("#consulta")

        self.send_button = page.locator(
            'button[type="submit"]'
        )

        self.conversation = page.get_by_role(
            "region",
            name="Conversación"
        )

        self.loading_message = page.get_by_text(
            "Buscando en el catálogo y armando la recomendación…",
            exact=True
        )

                # Botón dentro de la conversación
        self.new_conversation_button = self.conversation.get_by_role(
            "button",
            name="+ Nueva conversación",
            exact=True
        )

        # Botón del aviso de conversación recuperada
        self.previous_conversation_notice = page.get_by_role(
            "status"
             ).filter(has_text="Continuamos tu conversación anterior.")

        self.recovered_new_conversation_button = (
            self.previous_conversation_notice.get_by_role(
                "button",
                name="+ Nueva conversación",
                exact=True
            )
        )

    def open_assistant(self):
        self.open("/asistente")

    def write_query(self, query: str):
        self.query_input.fill(query)

    def send_query(self):
        expect(self.send_button).to_be_enabled()
        self.send_button.click()

    def wait_for_response(self):
        expect(
            self.loading_message
        ).to_be_hidden(timeout=90000)

    def get_conversation_text(self):
        return self.conversation.inner_text()

    def start_new_conversation(self):
        self.new_conversation_button.click()

    def is_query_input_empty(self):
        return self.query_input.input_value() == ""

    def reload_assistant(self):
        self.page.reload()

    def start_new_conversation_from_notice(self):
        self.recovered_new_conversation_button.click()