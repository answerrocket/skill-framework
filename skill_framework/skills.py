import inspect
import jinja2
import os
from pydantic import BaseModel, ConfigDict
from types import SimpleNamespace
from typing import Callable
from skill_framework.util import flexible_decorator


class FrameworkBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)


class SkillParameter(FrameworkBaseModel):
    name: str
    constrained_to: str | None = None
    is_multi: bool = False


class SkillParameters:
    def __init__(self, assistant_id, **kwargs):
        self.assistant_id = assistant_id
        self.arguments = SimpleNamespace(**kwargs)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class SkillOutput(FrameworkBaseModel):
    final_prompt: str | None
    "Used to prompt the model to generate the chat response"

    narrative: str | None
    "A text element that can accompany the visualization. Markdown formatting supported."

    visualization: str | None
    "A rendered json layout payload"


class Skill:
    def __init__(self, fn: Callable[[SkillParameters], SkillOutput], name=None, description=None, parameters=None):
        self.fn = fn
        self.parameters = parameters or []
        self.name = name or fn.__name__
        self.description = description
        self.nodes = []

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def node(self, fn):
        n = Node(fn, skill=self)
        self.nodes.append(n)
        return n


class Node:
    def __init__(self, fn, name=None, skill=None):
        self.fn = fn
        self.name = name or fn.__name__
        self.skill = skill
        self.signature = inspect.signature(fn)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


@flexible_decorator
def skill(fn: Callable[[SkillParameters], SkillOutput], name: str = None, parameters: list[SkillParameter] | None = None, description: str = None):
    """
    Marks a function as a skill entrypoint.
    """
    return Skill(fn, name=name, parameters=parameters, description=description)


def render(template: jinja2.Template, variables: dict):
    """
    Merges skill-provided context with builtin context and renders the template.
    :param template: a jinja template for the layout to be rendered
    :param variables: what should be rendered into the template.
    :return:
    """
    base_vars = {
        'MAX__RESOURCES': os.getenv('MAX_RESOURCES') or '/resources/'
    }
    return template.render({**base_vars, **variables})
