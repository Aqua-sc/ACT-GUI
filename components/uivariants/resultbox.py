from nicegui import ui

class ResultBox:
    def __init__(self, title: str = "Result", on_toggle=None):
        self.expanded = False
        self.on_toggle=on_toggle

        with ui.column().classes("w-full gap-1") as self.root:
            with ui.row().classes("items-center cursor-pointer select-none") as self.header:
                self.arrow = ui.icon("chevron_right").classes("cursor-pointer")
                self.title_label = ui.label(title).classes("font-semibold")

            self.content = ui.column().classes("pl-4 hidden")
            with self.content:
                self.content_label = ui.label("Result").classes("text-sm whitespace-pre-wrap font-mono")
        
        self.header.on("click", self.toggle)

    def toggle(self):
        self.expanded = not self.expanded

        if self.expanded:
            self.arrow.set_name("expand_more")
            self.content.classes(remove="hidden")
        else:
            self.arrow.set_name("chevron_right")
            self.content.classes(add="hidden")

        if self.on_toggle:
            self.on_toggle(self.expanded)
    
    def set_title(self, title: str):
        self.title_label.set_text(title)
    
    def set_content(self, content: str):
        self.content_label.set_text(content)