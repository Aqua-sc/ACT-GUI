from typing import List

import plotly.graph_objects as go
from nicegui import ui

from components import ComponentInterface

class PieChartComponent:
    def __init__(self, components):
        self.components = components
        self.chart = None
        self.fig = None

    def build_ui(self):

        self.fig = go.Figure(
            data=[go.Pie(labels=[], values=[], hole=0.3)]
        )

        self.chart = ui.plotly(self.fig).classes('w-full h-96')

        self.refresh(self.components)

    def refresh(self, components):

        self.components = components

        labels = [c.get_label() for c in components]
        values = [c.compute() for c in components]

        self.fig.data[0].labels = labels
        self.fig.data[0].values = values

        self.chart.update()