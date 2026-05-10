from enum import Enum
from typing import List

import plotly.graph_objects as go
from nicegui import ui

from components import ComponentInterface
from components.overwrites import OverwriteInfo, OVERWRITE_TYPE

class ComparingPlotComponent:
    def __init__(self, components):
        self.components : List[ComponentInterface] = components
        self.graph_type = self.GRAPH_TYPE.BAR
        self.overwrite : OverwriteCard | None = None
        self.chart = None
        self.fig = None

    class GRAPH_TYPE(Enum):
        BAR = 1
        LINE = 2

    def get_component_labels(self) -> List[str]:
        return [c.get_label() for c in self.components]
    
    def find_component_by_label(self, label: str) -> ComponentInterface | None:
        for component in self.components:
            if component.get_label() == label:
                return component

        return None

    def on_component_select_change(self, e):
        label = e.value

        component = self.find_component_by_label(label)
        if (component):
            if self.overwrite:
                self.overwrite.refresh(component)
            else:
                self.overwrite = OverwriteCard(component, self.refresh_graph)
        
        self.render_overwrite_card()
    
    def on_graph_select_change(self, e):
        self.graph_type = self.GRAPH_TYPE[e.value]
        self.refresh_graph()

    def render_overwrite_card(self):
        self.overwrite_container.clear()

        if self.overwrite is None:
            return

        with self.overwrite_container:
            self.overwrite.build_ui()

    def refresh(self, components: List[ComponentInterface]):
        self.components = components
        labels = self.get_component_labels()

        self.component_select.options = labels
        self.component_select.update()

        if (
            self.overwrite is not None
            and self.overwrite.get_component() not in self.components
        ):
            self.overwrite = None
            self.component_select.value = None
            self.component_select.update()

            self.overwrite_container.clear()
        elif self.overwrite is not None:
            self.render_overwrite_card()

        self.refresh_graph()

    def compute_scenario(self, overwrite_value=None):
        values = []

        target = self.overwrite.get_component() if self.overwrite else None

        for c in self.components:
            if target and c == target and overwrite_value is not None:
                values.append(overwrite_value)
            else:
                values.append(c.compute())

        return values

    def refresh_graph(self):
        self.fig.data = []

        overwrite_values = self.overwrite.get_values() if self.overwrite else []
        title, labels = self.overwrite.get_labels() if self.overwrite else ("", [])

        if self.graph_type == self.GRAPH_TYPE.BAR:
            if overwrite_values:
                for i, ov in enumerate(overwrite_values):
                    values = self.compute_scenario(ov)
                    for c, v in zip(self.components, values):
                        self.fig.add_trace(
                            go.Bar(
                                x=[labels[i]] if labels else [f"Scenario {i}"],
                                y=[v],
                                name=c.get_label(),
                                marker=dict(color=c.get_color()),
                                showlegend=(i == 0)
                            )
                        )
                
                self.fig.update_layout(
                    xaxis_title=title if title else "Selected scenario's",
                    yaxis_title="Carbon (g CO2)"
                )
            else:
                values = self.compute_scenario()
                for c, v in zip(self.components, values):
                    self.fig.add_trace(
                        go.Bar(
                            x=["Base"],
                            y=[v],
                            name=c.get_label(),
                            marker=dict(color=c.get_color())
                        )
                    )

                self.fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Carbon (g CO2)"
                )
            self.fig.update_layout(barmode="stack")

        elif self.graph_type == self.GRAPH_TYPE.LINE:
            if overwrite_values:
                x_vals = []
                y_vals = []
                for i, ov in enumerate(overwrite_values):
                    values = self.compute_scenario(ov)
                    total = sum(values)

                    x_vals.append(labels[i] if labels else f"Scenario {i}")
                    y_vals.append(total)
            
                self.fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode="lines+markers",
                        name="Total",
                        showlegend=False
                    )
                )

                self.fig.update_layout(
                    xaxis_title=title if title else "Selected scenario's",
                    yaxis_title="Total Carbon (g CO2)"
                )

            else:
                total = sum(self.compute_scenario())
                self.fig.add_trace(
                    go.Scatter(
                        x=["Base"],
                        y=[total],
                        mode="lines+markers"
                    )
                )

                self.fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Total Carbon (g CO2)"
                )
            
        self.fig.update_layout(
            yaxis=dict(rangemode="tozero")
        )
        self.chart.update()

    def build_ui(self):
        with ui.row():
            with ui.column():
                with ui.row():
                    self.component_select = ui.select(
                        options=self.get_component_labels(),
                        label="Select component",
                        on_change=self.on_component_select_change,
                    ).classes("w-64")

                    self.graph_select = ui.select(
                        options=[t.name for t in self.GRAPH_TYPE],
                        value=self.graph_type.name,
                        label="Select graph type",
                        on_change=self.on_graph_select_change,
                    )

                self.overwrite_container = ui.column()
            
            self.fig = go.Figure()
            self.chart = ui.plotly(self.fig).classes('w-96 h-96')

        self.refresh(self.components)

class OverwriteCard:
    def __init__(self, component: ComponentInterface, refreshcallback: callable):
        self.component : ComponentInterface = component
        self.overwrites : List[OverwriteInfo] = component.get_overwrites()
        self.selected_overwrite = self.overwrites[1] if len(self.overwrites) > 0 else None
        self.selected_values = []
        self.refreshcallback = refreshcallback

    def get_component(self) -> ComponentInterface:
        return self.component
    
    def find_overwrite_from_field(self, field) -> OverwriteInfo | None:
        for owi in self.overwrites:
            if owi.field == field:
                return owi

        return None
    
    def refresh_selected(self, e):
        owi = self.find_overwrite_from_field(e.value)
        if not owi:
            return
        self.selected_overwrite = owi
        self.selected_values = []
        self.container.clear()

        with self.container:
            self.build_overwrites()
        
    def refresh(self, component: ComponentInterface):
        self.component = component
        self.overwrites : List[OverwriteInfo] = component.get_overwrites()
        self.overwrites = self.overwrites if self.overwrites else []
        self.selected_overwrite = self.overwrites[1] if len(self.overwrites) > 0 else None
        self.selected_values = []
        
        self.overwrite_select.options = [x.field for x in self.overwrites]
        self.overwrite_select.value = self.selected_overwrite.field

        self.container.clear()

        with self.container:
            self.build_overwrites()

    def get_values(self):
        return [self.component.compute_changed(**{self.selected_overwrite.field: x}) for x in self.selected_values]

    def get_labels(self):
        return (
            f"{self.component.get_label()} {self.selected_overwrite.field.replace("_", " ")}", 
            [str(x) for x in self.selected_values]
        )
    
    def build_ui(self):
        with ui.card().classes("w-96 gap-4"):
            self.overwrite_select = ui.select(
                options=[x.field for x in self.overwrites],
                value=self.selected_overwrite.field,
                label="Select value",
                on_change=self.refresh_selected
            ).classes("w-full")

            self.container = ui.column().classes(
                "w-full gap-4"
            )

            with self.container:
                self.build_overwrites()

    def build_overwrites(self):
        if not self.selected_overwrite:
            return
        
        ui.label(self.selected_overwrite.field)

        if (self.selected_overwrite.type == OVERWRITE_TYPE.DROPDOWN_STR):
            self.build_dropdown_overwrite()
        elif (self.selected_overwrite.type == OVERWRITE_TYPE.RANGED_FP):
            self.build_ranged_overwrite()

    def build_dropdown_overwrite(self):
        overwrite = self.selected_overwrite
        self.selected_values
        available_options = [v for v in overwrite.values_str if v not in self.selected_values]

        chips_container = ui.row().classes("gap-2")

        select = ui.select(
            options=available_options,
            label="Select value"
        ).classes("w-full")

        def refresh_ui():
            select.options = [v for v in overwrite.values_str if v not in self.selected_values]

            select.value = None
            select.update()

            chips_container.clear()

            with chips_container:
                for value in self.selected_values:
                    with ui.chip().props(
                        "removable"
                    ) as chip:
                        ui.label(value)

                        def remove_value(v=value):
                            self.selected_values.remove(v)
                            refresh_ui()

                        chip.on("remove", remove_value)
            
            self.refreshcallback()

        def on_select(e):
            value = e.value
            if (
                value is not None
                and value not in self.selected_values
            ):
                self.selected_values.append(value)

            refresh_ui()

        select.on_value_change(on_select)
        refresh_ui()

    def build_ranged_overwrite(self):
        overwrite = self.selected_overwrite
        chips_container = ui.row().classes(
            "gap-2"
        )

        input_box = ui.input(
            label="Add value"
        ).props(
            "type=number"
        ).classes(
            "w-full"
        )

        input_box.on(
            "wheel",
            lambda e: None,
            js_handler="""
                (e) => {
                    e.target.blur()
                }
            """
        )

        input_box.on(
            "keydown.enter",
            lambda e: add_value()
        )

        def refresh_ui():
            self.selected_values.sort()
            chips_container.clear()

            with chips_container:
                for value in self.selected_values:
                    with ui.chip().props("removable") as chip:
                        ui.label(str(value))

                        def remove_value(v=value):
                            self.selected_values.remove(v)
                            refresh_ui()

                        chip.on("remove", remove_value)
            
            self.refreshcallback()

        def add_value():
            if input_box.value == "":
                return

            try:
                value = float(input_box.value)

                if (
                    overwrite.range_min is not None and value < overwrite.range_min
                ):
                    ui.notify(f"Minimum value is {overwrite.range_min}")
                    return

                if (
                    overwrite.range_max is not None and value > overwrite.range_max
                ):
                    ui.notify(f"Maximum value is {overwrite.range_max}")
                    return

                if value not in self.selected_values:
                    self.selected_values.append(value)
                else:
                    ui.notify("Value already added")

                input_box.value = None
                input_box.update()

                refresh_ui()

            except Exception as e:
                print(e)
                ui.notify(
                    "Please enter a valid number"
                )

        ui.button(
            "Add",
            on_click=add_value
        )

        refresh_ui()