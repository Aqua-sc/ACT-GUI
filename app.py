from enum import Enum
from typing import List

from components import ComponentInterface, ICComponent, PieChartComponent, DRAMComponent, SSDComponent, HDDComponent
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

components: List[ComponentInterface] = []

components_column = None
chart_container = None
total_label = None
piechart = PieChartComponent(components[::])

def refresh():
    try: 
        error_label.set_text("")

        for component in components:
            component.refresh()
    
        piechart.refresh(components)

        total = sum([c.compute() for c in components])
        total_label.set_text(f"Total Carbon: {format_carbon(total)}")
    except:
        error_label.set_text(f"Error during refresh")

def delete(component: ComponentInterface):
    components.remove(component)
    refresh()

def add_component(type: COMPONENT_TYPE):
    if type == COMPONENT_TYPE.IC:
        component = ICComponent(refreshcallback=refresh, deletecallback=delete)
    elif type == COMPONENT_TYPE.DRAM:
        component = DRAMComponent(refreshcallback=refresh, deletecallback=delete)
    elif type == COMPONENT_TYPE.SSD:
        component = SSDComponent(refreshcallback=refresh, deletecallback=delete)
    elif type == COMPONENT_TYPE.HDD:
        component = HDDComponent(refreshcallback=refresh, deletecallback=delete)

    components.append(component)

    with components_column:
        component.build_ui()

    refresh()


with ui.column():
    with ui.row():
        with ui.column():
            ui.label("IC Footprint Calculator").classes(
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

            components_column = ui.row()

        with ui.column():
            total_label = ui.label(f"Total Carbon: {format_carbon(0)}")
            chart_container = ui.column().classes('w-full')

            with chart_container:
                piechart.build_ui()

ui.run()
