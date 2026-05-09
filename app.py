from typing import List

from components import ComponentInterface, ICComponent, PieChartComponent
from dram_model import Fab_DRAM
from logic_model import Fab_Logic
from nicegui import ui
import plotly.graph_objects as go
from ssd_model import Fab_SSD

components: List[ComponentInterface] = []

components_column = None
chart_container = None
piechart = PieChartComponent(components[::])

def refresh():
    try: 
        error_label.set_text("")

        for component in components:
            component.refresh()
    
        piechart.refresh(components)   
    except:
        error_label.set_text(f"Error during refresh: {e}")

def add_IC():
    component = ICComponent(refreshcallback=refresh)
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

            ui.button(
                "Add IC",
                on_click=add_IC,
            )

            components_column = ui.row()

        with ui.column().classes('flex-grow'):
            chart_container = ui.column().classes('w-full')

            with chart_container:
                piechart.build_ui()

ui.run()
