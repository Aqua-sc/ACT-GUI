from dataclasses import dataclass, replace
import random
from typing import List
from nicegui import ui
from ssd_model import Fab_SSD
from util import format_carbon
from components import ComponentInterface
from components.overwrites import OVERWRITE_TYPE, OverwriteInfo
from components.uivariants import no_scroll_number, ResultBox
import json


@dataclass
class SSDState:
    process_node: str
    fab_yield: float
    capacity: float

class SSDComponent(ComponentInterface):
    def __init__(
        self, 
        refreshcallback: callable, 
        deletecallback: callable,
        color: str
    ):

        self.PROCESS_NODES = self.get_process_nodes()

        self.state = SSDState(
            process_node=self.PROCESS_NODES[0],
            fab_yield=0.875,
            capacity=0
        )
            
        self.label = "SSD_" + str(random.randint(0, 1000))

        self.result = None
        self.refreshcallback = refreshcallback
        self.deletecallback = deletecallback
        self.color = color

    def get_label(self):
        return self.label

    def get_color(self):
        return self.color

    def get_overwrites(self) -> List[OverwriteInfo]:
        return [
            OverwriteInfo(
                field="capacity",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0
            ),
            OverwriteInfo(
                field="process_node",
                type=OVERWRITE_TYPE.DROPDOWN_STR,
                values_str=self.PROCESS_NODES
            ),
            OverwriteInfo(
                field="fab_yield",
                type=OVERWRITE_TYPE.RANGED_FP,
                range_min=0.001,
                range_max=1
            )
        ]
    
    def get_process_nodes(self) -> List[str]:
        with open("ssd/ssd_hynix.json", 'r') as f:
            process_node_map = json.load(f)

        with open("ssd/ssd_seagate.json", 'r') as f:
            process_node_map.update(json.load(f))

        with open("ssd/ssd_western.json", 'r') as f:
            process_node_map.update(json.load(f))
            
        return list(process_node_map.keys())

    def compute(self) -> float:
        return self._compute(self.state, save_logic=True)
    
    def get_computation(self) -> str:
        if not self.logic:
            return ""
        else:
            return self.logic.get_computation_string()
    
    def _compute(self, state: SSDState, save_logic=False):
        logic = Fab_SSD(
            config=state.process_node,
            fab_yield=state.fab_yield
        )

        logic.set_capacity(state.capacity)

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
        if e.value != 0 and not e.value:
            value = None
        else:
            value = max(0.001, min(1.0, float(e.value)))
            self.update_state(fab_yield=value)

        self.yield_input.value = value
        self.yield_input.update()
    
    async def on_capacity_change(self, e):
        if e.value != 0 and not e.value:
            value = None
        else:
            value = max(0.0, float(e.value))
            self.update_state(capacity=value)

        self.capacity_input.value = value
        self.capacity_input.update()

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
        self.card = ui.card().classes("overflow-y-auto max-h-[calc(100vh-220px-1.5rem)] min-w-50 border-4 bg-white").style(
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

            self.capacity_input = no_scroll_number(
                "Capacity (GB)",
                value=self.state.capacity,
                step=0.5,
                min=0,
                validation={
                    'Must be positive': lambda v: not v or 0 <= float(v)
                },
                on_change=self.on_capacity_change,
            ).classes('w-full')

            ui.select(
                options=self.PROCESS_NODES,
                value=self.state.process_node,
                label="Process node",
                on_change=lambda e: self.update_state(process_node=e.value),
            ).classes('w-full')

            self.yield_input = no_scroll_number(
                "Fab yield",
                value=self.state.fab_yield,
                min=0.001,
                max=1,
                step=0.01,
                validation={
                    'Must be between 0 and 1': lambda v: not v or 0 < float(v) <= 1
                },
                on_change=self.on_yield_change,
            ).classes('w-full')

            self.result_label = ResultBox("Result", on_toggle=self.update_width)

        self.refresh()

