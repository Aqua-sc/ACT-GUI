
from dataclasses import dataclass, replace
import json
from typing import List

from nicegui import ui
from components.overwrites import OVERWRITE_TYPE, OverwriteInfo
from components.uivariants import no_scroll_number, ResultBox
from operational_model import Operational_Logic
from util import format_carbon

@dataclass
class OFState:
    carbon_intensity: str
    energy: float


class OperationalComponent:
    def __init__(self, refreshcallback: callable):
        self.CARBON_INTENSITIES = self.get_carbon_intensities()

        self.state = OFState(
            carbon_intensity=self.CARBON_INTENSITIES[0],
            energy=0
        )
        self.refreshcallback = refreshcallback
        self.result = None
        self.color = "#000000"
        self.label = "Operational FP"

    def get_overwrites(self) -> List[OverwriteInfo]:
        return [
            OverwriteInfo(
                field="energy",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0
            ),
            OverwriteInfo(
                field="carbon_intensity",
                type=OVERWRITE_TYPE.DROPDOWN_STR,
                values_str=self.CARBON_INTENSITIES
            ),
        ]

    def get_label(self):
        return self.label
    
    def get_color(self):
        return self.color

    def get_carbon_intensities(self):
        keys = []
        with open("carbon_intensity/source.json") as f:
            carbon_intensity_map = json.load(f)
            keys.extend(
                [ "src_" + k for k in carbon_intensity_map.keys()]
            )
        with open("carbon_intensity/location.json") as f:
            carbon_intensity_map = json.load(f)
            keys.extend(
                [ "loc_" + k for k in carbon_intensity_map.keys()]
            )
        return keys

    def compute(self) -> float:
        return self._compute(self.state, save_logic=True)
    
    def compute_changed(self, **kwargs):
        new_state = replace(self.state, **kwargs)
        return self._compute(new_state)
    
    def get_computation(self) -> str:
        if not self.logic:
            return ""
        else:
            return self.logic.get_computation_string()

    def _compute(self, state: OFState, save_logic=False):
        logic = Operational_Logic(
            carbon_intensity=state.carbon_intensity,
            energy=state.energy
        )

        if save_logic:
            self.logic = logic

        return logic.get_carbon()
    
    def refresh(self) -> None:
        result = self.compute()

        self.result_label.set_title(
            format_carbon(result)
        )

        self.result_label.set_content(
            self.get_computation()
        )

    def update_state(self, **kwargs):
        self.state = replace(self.state, **kwargs)
        self.refreshcallback()

    async def on_intensity_change(self, e):
        if e.value != 0 and not e.value:
            value = None
        else:
            value = max(0.0, float(e.value))
            self.packing_intensity = value

        self.intensity_input.value = value
        self.intensity_input.update()

        self.refreshcallback()

    async def on_energy_change(self, e):
        if e.value != 0 and not e.value:
            value = None
        else:
            value = max(0.0, float(e.value))
            self.update_state(energy=value)

        self.energy_input.value = value
        self.energy_input.update()

        self.refreshcallback()
    
    def build_ui(self):
        with ui.column().classes("flex-1 flex-row gap-2"):
            self.energy_input = no_scroll_number(
                    "Energy (kWh)",
                    value=self.state.energy,
                    step=1,
                    min=0,
                    validation={
                        'Must be positive': lambda v: not v or 0 <= float(v)
                    },
                    on_change=self.on_energy_change
                ).classes("w-32")
            
            ui.select(
                    options=self.CARBON_INTENSITIES,
                    value=self.state.carbon_intensity,
                    label="Carbon intensity",
                    on_change=lambda e: self.update_state(carbon_intensity=e.value),
                ).classes("w-48")
        
            self.result_label = ResultBox("Result")

        self.refresh()