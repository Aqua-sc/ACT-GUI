from enum import Enum
from typing import List

from components import (
    PackingComponent,
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

PALETTE =  [ # Generated using https://mokole.com/palette.html
    '#7fffd4',
    '#ffa07a',  
    '#dda0dd',  
    '#f0e68c',  
    '#ff00ff',  
    '#adff2f',  
    '#0000ff',  
    '#00bfff',  
    '#4169e1',  
    '#00ff7f',  
    '#c71585',  
    '#ffd700',  
    '#ff8c00',  
    '#ff0000',  
    '#00008b',  
    "#808000",  
    "#7f0000",  
    '#2e8b57',  
    '#2f4f4f',  
    '#dcdcdc',  
]

MAX_COMPONENTS = len(PALETTE)

components: List[ComponentInterface] = []

components_row = None
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

        total = sum([c.compute() for c in components]) + len(components) * packingcomponent.packing_intensity
        total_label.set_text(f"Total Carbon: {format_carbon(total)}")
    except Exception as e:
        error_label.set_text(f"Error during refresh: {e}")

packingcomponent = PackingComponent(refreshcallback=refresh)

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

ui.add_head_html('''
    <style>
    .q-layout, .q-page {
        min-height: 0 !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    .q-page-container, .nicegui-content {
        height: 100% !important;
        overflow: hidden !important;
    }
    </style>
''')

with ui.column().classes("h-full overflow-hidden min-w-0 w-[100vw]"):
    
    with ui.row().classes("w-full flex-row justify-between place-items-center"):
        with ui.row():
            ui.label("ACT: Architectural Carbon Modeling Tool").classes(
                            'text-2xl font-bold'
                        )
            
            error_label = ui.label().classes('text-red-600')
        
        total_label = ui.label(f"Total Carbon: {format_carbon(0)}")
        
    with ui.row().classes("h-20"):
        packingcomponent.build_ui()
        # TODO: OPP
    
    with ui.row().classes("flex-nowrap min-w-0 h-full"):
        with ui.column().classes("flex-1 h-full"):
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
                "flex-nowrap max-w-[42vw] overflow-x-auto p-3 gap-3 h-full items-start"
            )
        with ui.row().classes(
            "flex-nowrap min-w-0 max-w-[53vw] overflow-x-auto overflow-y-auto p-3 gap-3"
        ):
            piechart.build_ui()
            comparingPlot.build_ui()

ui.run(title='ACT', favicon="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn-icons-png.flaticon.com%2F512%2F6859%2F6859918.png&f=1&nofb=1&ipt=c142a04ad55371696e010c6739a262a017330d994151ebf5091859e898146c45")
