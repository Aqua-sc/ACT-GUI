# custom_inputs.py

from typing import Callable

from nicegui import ui
from nicegui.defaults import DEFAULT_PROP, DEFAULT_PROPS
from nicegui.events import ValueChangeEventArguments
from nicegui.elements.input import Input
from nicegui.elements.number import Number
from nicegui.elements.mixins.validation_element import (
    ValidationDict,
    ValidationFunction,
)
from nicegui.elements.mixins.value_element import Handler


def no_scroll_number(
    label: str | None = DEFAULT_PROP | None,
    *,
    placeholder: str | None = DEFAULT_PROP | None,
    value: float | None = DEFAULT_PROPS['model-value'] | None,
    min: float | None = DEFAULT_PROP | None,
    max: float | None = DEFAULT_PROP | None,
    precision: int | None = None,
    step: float | None = DEFAULT_PROP | None,
    prefix: str | None = DEFAULT_PROP | None,
    suffix: str | None = DEFAULT_PROP | None,
    format: str | None = None,
    on_change: Handler[ValueChangeEventArguments[float | None]] | None = None,
    validation: ValidationFunction | ValidationDict | None = None,
) -> Number:

    number_box = ui.number(
        label=label,
        placeholder=placeholder,
        value=value,
        min=min,
        max=max,
        precision=precision,
        step=step,
        prefix=prefix,
        suffix=suffix,
        format=format,
        on_change=on_change,
        validation=validation,
    )

    number_box.on(
        "wheel",
        lambda e: None,
        js_handler="""
            (e) => {
                e.target.blur()
            }
        """
    )

    return number_box


def no_scroll_input(
    label: str | None = DEFAULT_PROP | None,
    *,
    placeholder: str | None = DEFAULT_PROP | None,
    value: str | None = DEFAULT_PROP | '',
    password: bool = DEFAULT_PROP | False,
    password_toggle_button: bool = False,
    prefix: str | None = None,
    suffix: str | None = None,
    on_change: Handler[ValueChangeEventArguments[str | None]] | None = None,
    autocomplete: list[str] | None = DEFAULT_PROPS['_autocomplete'] | None,
    validation: ValidationFunction | ValidationDict | None = None,
) -> Input:

    input_box = ui.input(
        label=label,
        placeholder=placeholder,
        value=value,
        password=password,
        password_toggle_button=password_toggle_button,
        prefix=prefix,
        suffix=suffix,
        on_change=on_change,
        autocomplete=autocomplete,
        validation=validation,
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

    return input_box