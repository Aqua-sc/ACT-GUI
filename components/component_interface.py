class ComponentInterface:
    def get_label(self) -> str:
        pass

    def compute(self) -> float:
        pass

    def refresh(self) -> None:
        pass

    def build_ui(self) -> None:
        pass