from dram_model import Fab_DRAM
from logic_model import Fab_Logic
from nicegui import ui
import plotly.graph_objects as go
from ssd_model import Fab_SSD

# =====================================
# Global state
# =====================================

state = {
    'process_node': 28,
    'ic_area': 120,
    'cpu_area': 35,
    'ram': 6,
    'storage': 128,
    'auto_recalculate': True,
}


# =====================================
# Calculation function
# =====================================

results_labels = {}
chart = None


def refresh():
    global chart

    if not state['auto_recalculate']:
        return

    results = compute()

    for key, value in results.items():
        results_labels[key].set_text(f'{key}: {value:.2f} g CO2')

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(results.keys())[:-1],
                y=[results[k] for k in list(results.keys())[:-1]],
            )
        ]
    )

    chart.update_figure(fig)

# =====================================
# UI
# =====================================

with ui.row():
    with ui.column().classes('w-96'):
        ui.label('IC Footprint Calculator').classes('text-2xl font-bold')

        ui.number(
            'Process node (nm)',
            value=state['process_node'],
            on_change=lambda e: update_state('process_node', e.value),
        )

        ui.number(
            'IC area',
            value=state['ic_area'],
            on_change=lambda e: update_state('ic_area', e.value),
        )

        ui.number(
            'CPU area',
            value=state['cpu_area'],
            on_change=lambda e: update_state('cpu_area', e.value),
        )

        ui.number(
            'RAM capacity (GB)',
            value=state['ram'],
            on_change=lambda e: update_state('ram', e.value),
        )

        ui.number(
            'Storage capacity (GB)',
            value=state['storage'],
            on_change=lambda e: update_state('storage', e.value),
        )

        ui.checkbox(
            'Auto recalculate',
            value=True,
            on_change=lambda e: update_state('auto_recalculate', e.value),
        )

        ui.button('Manual Recalculate', on_click=refresh)

    with ui.column():

        for name in ['IC', 'CPU', 'DRAM', 'SSD', 'Packaging', 'Total']:
            results_labels[name] = ui.label()

        chart = ui.plotly(go.Figure())


def compute():
    IC_Logic = Fab_Logic(
        gpa='95',
        carbon_intensity='src_coal',
        process_node=state['process_node'],
        fab_yield=0.95,
    )

    CPU_Logic = Fab_Logic(
        gpa='95',
        carbon_intensity='src_coal',
        process_node=state['process_node'],
        fab_yield=0.95,
    )

    DRAM = Fab_DRAM(
        config='ddr3_50nm',
        fab_yield=0.95,
    )

    SSD = Fab_SSD(
        config='nand_30nm',
        fab_yield=0.95,
    )

    IC_Logic.set_area(state['ic_area'])
    CPU_Logic.set_area(state['cpu_area'])
    DRAM.set_capacity(state['ram'])
    SSD.set_capacity(state['storage'])

    packaging = 10 * 150

    results = {
        'IC': IC_Logic.get_carbon(),
        'CPU': CPU_Logic.get_carbon(),
        'DRAM': DRAM.get_carbon(),
        'SSD': SSD.get_carbon(),
        'Packaging': packaging,
    }

    results['Total'] = sum(results.values())

    return results


# =====================================
# Helper
# =====================================


def update_state(key, value):
    state[key] = value

    if state['auto_recalculate']:
        refresh()


# Initial calculation
refresh()


ui.run()