from typing import List
from components.overwrites import OverwriteInfo


class ComponentInterface:
    def get_label(self) -> str:
        pass
    
    def get_color(self) -> str:
        pass

    def compute(self) -> float:
        pass

    def refresh(self) -> None:
        pass

    def build_ui(self) -> None:
        pass

    def compute_changed(self, **kwargs) -> float:
        pass
    
    def get_overwrites(self) -> List[OverwriteInfo]:
        pass

    def change_max_height(self, offset):
        self.card.classes(remove=self.maxheightclass)
        self.maxheightclass=f"max-h-[calc(100vh-{offset}px-1.5rem)]"
        self.card.classes(add=self.maxheightclass)
