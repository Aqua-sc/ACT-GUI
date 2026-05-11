
from nicegui import ui
from components.uivariants import no_scroll_number


class ApplicationComponent:
    def __init__(self, refreshcallback: callable):
        self.refreshcallback = refreshcallback
        self.lifetime = 0
        self.runtime = 0
        self.enabled = False

    def get_factor(self):
        if not self.enabled:
            return 1
        elif self.runtime == 0:
            return 0
        else:
            return self.runtime/self.lifetime
    
    async def on_lifetime_change(self, e):
        value = max(0.0, float(e.value))

        self.lifetime = value

        self.lifetime_input.value = value
        self.lifetime_input.update()

        self.refreshcallback()

    async def on_runtime_change(self, e):
        value = max(0.0, float(e.value))

        self.runtime = value

        self.runtime_input.value = value
        self.runtime_input.update()

        self.refreshcallback()

    def on_enabled_change(self, e):
        self.enabled = e.value
        self.refreshcallback()
    
    def build_ui(self):
        with ui.row():
            ui.checkbox(
                "", 
                value=False, 
                on_change=self.on_enabled_change
            )

            self.runtime_input = no_scroll_number(
                    "Runtime (h)",
                    value=self.runtime,
                    step=0.5,
                    min=0,
                    validation={
                        'Must be positive': lambda v: 0 <= float(v)
                    },
                    on_change=self.on_runtime_change
            ).classes("w-32")

            self.lifetime_input = no_scroll_number(
                    "Lifetime (h)",
                    value=self.lifetime,
                    step=1,
                    min=0,
                    validation={
                        'Must be positive': lambda v: 0 <= float(v)
                    },
                    on_change=self.on_lifetime_change
            ).classes("w-32")
