from dataclasses import dataclass, replace
import random
from typing import List
from nicegui import ui
from util import format_carbon
from components import ComponentInterface
from components.overwrites import OVERWRITE_TYPE, OverwriteInfo
from components.uivariants import no_scroll_number, ResultBox
from logic_model import Fab_Logic
import json


@dataclass
class ICState:
    gpa: str
    mpa: str | None
    carbon_intensity: str
    process_node: str
    fab_yield: float
    area: float

class ICComponent(ComponentInterface):
    def __init__(
        self, 
        refreshcallback: callable, 
        deletecallback: callable,
        color: str,
    ):

        self.PROCESS_NODES = self.get_process_nodes()
        self.CARBON_INTENSITIES = self.get_carbon_intensities()
        self.GPAS = self.get_gpas()

        self.state = ICState(
            gpa=self.GPAS[0],
            mpa=None,
            carbon_intensity=self.CARBON_INTENSITIES[0],
            process_node=self.PROCESS_NODES[0].removesuffix("nm"),
            fab_yield=0.875,
            area=0
        )
            
        self.label = "IC_" + str(random.randint(0, 1000))

        self.result = None
        self.refreshcallback = refreshcallback
        self.deletecallback = deletecallback
        self.color = color

    def get_overwrites(self) -> List[OverwriteInfo]:
        return [
            OverwriteInfo(
                field="area",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0
            ),
            OverwriteInfo(
                field="gpa",
                type=OVERWRITE_TYPE.DROPDOWN_STR,
                values_str=self.GPAS
            ),
            OverwriteInfo(
                field="mpa",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0
            ),
            OverwriteInfo(
                field="process_node",
                type=OVERWRITE_TYPE.DROPDOWN_STR,
                values_str=self.PROCESS_NODES
            ),
            OverwriteInfo(
                field="carbon_intensity",
                type=OVERWRITE_TYPE.DROPDOWN_STR,
                values_str=self.CARBON_INTENSITIES
            ),
            OverwriteInfo(
                field="fab_yield",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0.001,
                range_max=1
            )
        ]
        
    def get_label(self):
        return self.label
    
    def get_color(self):
        return self.color
    
    def get_gpas(self) -> List[int]:
        return ["95", "97", "99"]
    
    def get_process_nodes(self) -> List[str]:
        with open("logic/gpa_95.json", "r") as f:
            process_node_map = json.load(f)
            return list(process_node_map.keys())
        
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
        if "process_node" in kwargs:
            kwargs["process_node"] = (
                str(kwargs["process_node"])
                .removesuffix("nm")
            )

        new_state = replace(self.state, **kwargs)
        return self._compute(new_state)
    
    def get_computation(self) -> str:
        if not self.logic:
            return ""
        else:
            return self.logic.get_computation_string()
    
    def _compute(self, state: ICState, save_logic=False):
        logic = Fab_Logic(
            gpa=state.gpa,
            mpa=state.mpa,
            carbon_intensity=state.carbon_intensity,
            process_node=state.process_node,
            fab_yield=state.fab_yield
        )

        logic.set_area(state.area)

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

    def set_label(self, value: str):
        self.label = value
        self.refreshcallback()

    async def on_yield_change(self, e):
        value = max(0.001, min(1.0, float(e.value)))

        self.update_state(fab_yield=value)

        self.yield_input.value = value
        self.yield_input.update()
    
    async def on_area_change(self, e):
        value = max(0.0, float(e.value))

        self.update_state(area=value)

        self.area_input.value = value
        self.area_input.update()

    async def on_mpa_change(self, e):
        value = max(0.0, float(e.value))

        self.update_state(mpa=value)

        self.mpa_input.value = value
        self.mpa_input.update()

    def delete(self):
        self.card.delete()
        self.deletecallback(self)

    def update_width(self, expanded: bool):
        expanded_classes = "max-w-[33vw] flex-none"
        if expanded:
            self.card.classes(add=expanded_classes)
        else:
            self.card.classes(remove=expanded_classes)

    def build_ui(self):
        self.maxheightclass="max-h-[calc(100vh-220px-1.5rem)]"
        self.card = ui.card().classes(
            f"overflow-y-auto {self.maxheightclass} min-w-50 border-4 bg-white"
        ).style(
            f"border-color: {self.color}"
        )
        with self.card:
            with ui.row().classes("w-full sticky top-0 bg-white z-10 border-b-2 border-gray-500"):
                self.label_input = ui.input(
                    value=self.label,
                    on_change=lambda e: self.set_label(e.value)
                ).props('borderless dense')

                ui.button(
                    icon='delete',
                    on_click=self.delete  
                ).props('flat round dense color=red').classes(
                    'absolute top-0 right-0'
                )

            self.area_input = no_scroll_number(
                "Area (cm²)",
                value=self.state.area,
                step=0.01,
                min=0,
                validation={
                    'Must be positive': lambda v: 0 <= float(v)
                },
                on_change=self.on_area_change
            ).classes("w-full")

            ui.select(
                options=self.PROCESS_NODES,
                value=self.state.process_node+"nm",
                label="Process node",
                on_change=lambda e: self.update_state(process_node=e.value.removesuffix("nm")),
            ).classes("w-full")

            ui.select(
                options=self.CARBON_INTENSITIES,
                value=self.state.carbon_intensity,
                label="Carbon intensity",
                on_change=lambda e: self.update_state(carbon_intensity=e.value),
            ).classes("w-full")

            ui.select(
                options=self.GPAS,
                value=self.state.gpa,
                label="GPA (% abadement)",
                on_change=lambda e: self.update_state(gpa=e.value)
            ).classes("w-full")

            self.mpa_input = no_scroll_number(
                "MPA (g)",
                value=self.state.mpa,
                step=20,
                min=0,
                validation={
                    'Must be positive': lambda v: 0 <= float(v)
                },
                on_change=self.on_mpa_change
            ).classes("w-full")

            self.yield_input = no_scroll_number(
                "Fab yield",
                value=self.state.fab_yield,
                min=0.001,
                max=1,
                step=0.01,
                validation={
                    'Must be between 0 and 1': lambda v: 0 < float(v) <= 1
                },
                on_change=self.on_yield_change,
            ).classes('w-full')

            self.result_label = ResultBox("Result", on_toggle=self.update_width)

        self.refresh()