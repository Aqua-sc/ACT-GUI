from typing import List

import plotly.graph_objects as go
from nicegui import ui

from components import ComponentInterface

class PieChartComponent:
    def __init__(self, components):
        self.components : List[ComponentInterface] = components
        self.chart = None
        self.fig = None

    def build_ui(self):

        self.fig = go.Figure(
            data=[go.Pie(labels=[], values=[], hole=0.3, marker=dict(colors=[]))]
        )

        self.chart = ui.plotly(self.fig).classes('w-96 h-96')

        self.refresh(self.components)

    def refresh(self, components: List[ComponentInterface]):

        self.components = components

        labels = [c.get_label() for c in components]
        values = [c.compute() for c in components]
        colors = [c.get_color() for c in components]

        self.fig.data[0].labels = labels
        self.fig.data[0].values = values
        self.fig.data[0].marker.colors = colors

        self.chart.update()