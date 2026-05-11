
from nicegui import ui
from components.uivariants import no_scroll_number


class PackingComponent:
    def __init__(self, refreshcallback: callable):
        self.refreshcallback = refreshcallback
        self.packing_intensity = 0 
    
    async def on_intensity_change(self, e):
        value = max(0.0, float(e.value));

        self.packing_intensity = value

        self.intensity_input.value = value
        self.intensity_input.update()

        self.refreshcallback()
    
    def build_ui(self):
        self.intensity_input = no_scroll_number(
                "Packing intensity (g CO2)",
                value=self.packing_intensity,
                step=50,
                min=0,
                validation={
                    'Must be positive': lambda v: 0 <= float(v)
                },
                on_change=self.on_intensity_change
        ).classes("w-64")