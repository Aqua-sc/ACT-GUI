from dataclasses import dataclass, replace
import random
from typing import List
from nicegui import ui
from hdd_model import Fab_HDD
from util import format_carbon
from components import ComponentInterface
from components.overwrites import OVERWRITE_TYPE, OverwriteInfo
from components.uivariants import no_scroll_number, ResultBox
import json


@dataclass
class HDDState:
    process_node: str
    capacity: float

class HDDComponent(ComponentInterface):
    def __init__(
        self, 
        refreshcallback: callable, 
        deletecallback: callable,
        color: str,
    ):

        self.PROCESS_NODES = self.get_process_nodes()

        self.state = HDDState(
            process_node=self.PROCESS_NODES[0],
            capacity=0
        )
            
        self.label = "HDD_" + str(random.randint(0, 1000))

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
            )
        ]
    
    def get_process_nodes(self) -> List[str]:
        with open("hdd/hdd_consumer.json", 'r') as f:
            process_node_map = json.load(f)

        with open("hdd/hdd_enterprise.json", 'r') as f:
            process_node_map.update(json.load(f))
            
        return list(process_node_map.keys())

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
    
    def _compute(self, state: HDDState, save_logic=False):
        logic = Fab_HDD(
            config=state.process_node
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

    async def on_capacity_change(self, e):
        value = max(0.0, float(e.value));

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
        self.card = ui.card().classes("overflow-y-auto max-h-[calc(100vh-200px-1.5rem)] min-w-50 border-4 bg-white").style(
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
                    'Must be positive': lambda v: 0 <= float(v)
                },
                on_change=self.on_capacity_change,
            ).classes('w-full')

            ui.select(
                options=self.PROCESS_NODES,
                value=self.state.process_node,
                label="Process node",
                on_change=lambda e: self.update_state(process_node=e.value),
            ).classes('w-full')

            self.result_label = ResultBox("Result", on_toggle=self.update_width)

        self.refresh()

