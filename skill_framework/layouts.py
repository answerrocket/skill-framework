import json
from typing import Any

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from skill_framework.skills import FrameworkBaseModel

# trying to keep these flexible but still define models that specify the fields the utility methods need to work with
layout_model_config = ConfigDict(
    alias_generator=to_camel,
    extra='ignore',
    # this combined with to_camel allows these models to be initialized from json with camel or snake cased fields
    populate_by_name=True)


class LayoutFieldPointer(FrameworkBaseModel):
    element_name: str
    field_name: str

    model_config = layout_model_config


class LayoutVariable(FrameworkBaseModel):
    name: str
    is_required: bool = False
    default_value: Any = None
    targets: list[LayoutFieldPointer]
    model_config = layout_model_config


class SkillLayout(FrameworkBaseModel):
    layout_json: dict
    input_variables: list[LayoutVariable]
    model_config = layout_model_config


def wire_layout(layout: dict, input_values: dict) -> str:
    """
    Use this to combine a visual layout with placeholder variables with the data to fill in those placeholders.
    :param layout: a dictionary containing the layout data. If the layout was passed in as a parameter or is embedded in
        the skill, it can simply be used as an argument to this function.
    :param input_values: a dictionary mapping values to variables in the provided layout.
    :return: the complete layout with values embedded
    """
    skill_layout = SkillLayout(**layout)
    layout_dict = skill_layout.layout_json

    def apply_wiring(element, field_name, value):
        parts = field_name.split(".")
        if len(parts) == 1:
            element[field_name] = value
        else:
            apply_wiring(element[parts[0]], ".".join(parts[1:]), value)
        return element

    for var in skill_layout.input_variables:
        var_value = input_values.get(var.name) or var.default_value
        if var_value is None:
            if var.is_required:
                raise ValueError(f"Required variable {var.name} is not provided")
            continue
        for target in var.targets:
            element_name = target.element_name
            field_name = target.field_name
            layout_dict["children"] = [
                apply_wiring(child, field_name, var_value) if element_name == child.get("name") else child for child
                in layout_dict["children"]]

    return json.dumps(layout_dict, indent=2)
