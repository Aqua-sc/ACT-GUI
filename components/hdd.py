from dataclasses import dataclass, replace
import random
from typing import List
from nicegui import ui
from hdd_model import Fab_HDD
from util import format_carbon
from components import ComponentInterface
import json


@dataclass
class HDDState:
    process_node: str
    capacity: float

class HDDComponent(ComponentInterface):
    def __init__(self, refreshcallback: callable, deletecallback: callable):

        self.PROCESS_NODES = self.get_process_nodes()

        self.state = HDDState(
            process_node=self.PROCESS_NODES[0],
            capacity=0
        )
            
        self.label = "HDD_" + str(random.randint(0, 1000))

        self.result = None
        self.refreshcallback = refreshcallback
        self.deletecallback = deletecallback

    def get_label(self):
        return self.label
    
    def get_process_nodes(self) -> List[str]:
        with open("hdd/hdd_consumer.json", 'r') as f:
            process_node_map = json.load(f)

        with open("hdd/hdd_enterprise.json", 'r') as f:
            process_node_map.update(json.load(f))
            
        return list(process_node_map.keys())

    def compute(self) -> float:
        logic = Fab_HDD(
            config=self.state.process_node,
        )

        logic.set_capacity(self.state.capacity)

        return logic.get_carbon()
    
    def refresh(self) -> None:
        result = self.compute()

        self.result_label.set_text(
            format_carbon(result)
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
    
    def build_ui(self):
        self.card = ui.card()
        with self.card:
            with ui.row():
                self.label_input = ui.input(
                    value=self.label,
                    on_change=lambda e: self.set_label(e.value)
                ).props('borderless dense')

                ui.button(
                    icon='delete',
                    on_click=self.delete  
                ).props('flat round dense color=red').classes(
                    'absolute top-2 right-2'
                )

            self.capacity_input = ui.number(
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

            self.result_label = ui.label("Result")

        self.refresh()

