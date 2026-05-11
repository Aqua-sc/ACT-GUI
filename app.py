from enum import Enum
from typing import List

from components import (
    ComponentInterface, ICComponent, DRAMComponent, SSDComponent, HDDComponent,
    PieChartComponent, ComparingPlotComponent
)
from dram_model import Fab_DRAM
from logic_model import Fab_Logic
from nicegui import ui
import plotly.graph_objects as go
from ssd_model import Fab_SSD
from util import format_carbon

class COMPONENT_TYPE(Enum):
    IC = 1
    DRAM = 2
    SSD = 3
    HDD = 4

PALETTE =  [
    '#1f77b4',
    '#ff7f0e',  
    '#2ca02c',  
    '#d62728',  
    '#9467bd',  
    '#8c564b',  
    '#e377c2',  
    '#7f7f7f',  
    '#bcbd22',  
    '#17becf',  

    '#393b79',  
    '#637939',  
    '#8c6d31',  
    '#843c39',  
    '#7b4173',  
    "#aadae8",  
    "#0a441b",  
    '#756bb1',  
    '#636363',  
    '#e6550d',  
]

MAX_COMPONENTS = len(PALETTE)

components: List[ComponentInterface] = []

components_row = None
chart_container = None
total_label = None
piechart = PieChartComponent(components)
comparingPlot = ComparingPlotComponent(components)

def refresh():
    try: 
        error_label.set_text("")

        for component in components:
            component.refresh()

        labels = [x.get_label() for x in components]
        if len(labels) != len(set(labels)):
            error_label.set_text(f"Make sure all components have a unique name")
    
        piechart.refresh(components)
        comparingPlot.refresh(components)

        total = sum([c.compute() for c in components])
        total_label.set_text(f"Total Carbon: {format_carbon(total)}")
    except Exception as e:
        error_label.set_text(f"Error during refresh: {e}")

def delete(component: ComponentInterface):
    PALETTE.append(component.get_color())
    components.remove(component)
    refresh()

def add_component(type: COMPONENT_TYPE):
    if len(PALETTE) == 0:
        error_label.set_text(f"Max amount of components reached: {len(components)}/{MAX_COMPONENTS}")
        return
    
    color = PALETTE.pop()
    if type == COMPONENT_TYPE.IC:
        component = ICComponent(
            refreshcallback=refresh, 
            deletecallback=delete,
            color = color
        )
    elif type == COMPONENT_TYPE.DRAM:
        component = DRAMComponent(
            refreshcallback=refresh, 
            deletecallback=delete,
            color = color
        )
    elif type == COMPONENT_TYPE.SSD:
        component = SSDComponent(
            refreshcallback=refresh, 
            deletecallback=delete,
            color = color
        )
    elif type == COMPONENT_TYPE.HDD:
        component = HDDComponent(
            refreshcallback=refresh, 
            deletecallback=delete,
            color = color
        )

    components.append(component)

    with components_row:
        component.build_ui()

    refresh()


with ui.column():
    with ui.row().classes("flex"):
        with ui.column().classes("flex-1"):
            ui.label("ACT: Architectural Carbon Modeling Tool").classes(
                'text-2xl font-bold'
            )

            error_label = ui.label().classes('text-red-600')

            with ui.row():
                ui.button(
                    "Add IC",
                    on_click=lambda _: add_component(COMPONENT_TYPE.IC),
                )

                ui.button(
                    "Add DRAM",
                    on_click=lambda _: add_component(COMPONENT_TYPE.DRAM)
                )

                ui.button(
                    "Add SSD",
                    on_click=lambda _: add_component(COMPONENT_TYPE.SSD)
                )

                ui.button(
                    "Add HDD",
                    on_click=lambda _: add_component(COMPONENT_TYPE.HDD)
                )

            components_row = ui.row().classes(
                "flex-nowrap max-w-[50vw] overflow-x-auto overflow-y-hidden p-3 gap-3"
            )
        with ui.column():
            total_label = ui.label(f"Total Carbon: {format_carbon(0)}")
            chart_container = ui.column().classes('w-full')

            with chart_container:
                piechart.build_ui()
                comparingPlot.build_ui()


ui.run(title='ACT', favicon="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn-icons-png.flaticon.com%2F512%2F6859%2F6859918.png&f=1&nofb=1&ipt=c142a04ad55371696e010c6739a262a017330d994151ebf5091859e898146c45")
