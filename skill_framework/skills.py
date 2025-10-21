import jinja2
import keyword
import os
from pydantic import BaseModel, ConfigDict, field_validator, Field, create_model
from typing import Callable, Literal, Any
from skill_framework.util import flexible_decorator


class FrameworkBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)


class SkillParameter(FrameworkBaseModel):
    """
    Used in the @skill decorator to define parameters for your skill.
    Attributes:
        name: the name of the parameter. this needs to be a valid python identifier, as these names are used to generate
            a dataclass that will contain the parameter arguments when your skill is invoked.
        constrained_to: limit the parameter to a particular type during LLM interpretation.
            valid values are 'metrics', 'dimensions', 'filters', 'date_filter', 'date_dimensions', or a dataset column
        is_multi: if true, multiple arguments can be assigned to this parameter, and its value will always be a list
        description: the parameter description that will appear in the UI
        constrained_values: if set, limits the valid arguments to this parameter to those in this list
        default_value: the default value to use for this parameter
        parameter_type: the top-level type of this parameter. 'chat' parameters are ones that are exposed when
            selecting a skill to run and extracting values from user queries. 'prompt' parameters are for prompts that
            are meant to be exposed for potential customization. 'code' parameters can hold valid json and serve as
            a way to expose generic config.

    """
    name: str
    constrained_to: str | None = None
    is_multi: bool = False
    parameter_type: Literal['chat', 'prompt', 'code', 'visualization'] = 'chat'
    description: str | None = None
    constrained_values: list[str] = Field(default_factory=list)
    default_value: Any | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not is_valid_parameter_name(v):
            raise ValueError('Parameter name must be a valid python identifier')
        return v


def is_valid_parameter_name(name: str) -> bool:
    return name.isidentifier() and not keyword.iskeyword(name)


class SkillInput:
    """
    Container for context and parameter arguments passed into the skill. Recommended to create this object with
    the Skill.create_input helper method,

    Attributes:
        assistant_id: the id of the assistant in which your skill is running
        arguments: the arguments for your skill's parameters extracted from, for example, a chat interaction. This is a
            generated dataclass at runtime, so you can use attribute-style access to refer to them. "empty" values will
            be populated based on your declared parameters. f. ex, a list parameter for which no arguments were captured
            will be initialized to an empty list.
    """

    def __init__(self, assistant_id, arguments):
        self.assistant_id = assistant_id
        self.arguments = arguments

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class ParameterDisplayDescription(FrameworkBaseModel):
    """
    Display information about arguments for a particular parameter. This can be used to make it
    clear to the user what values were understood from the question or what defaults were used.
    Attributes:
        key: a unique key to identify this parameter. not part of what is displayed in the UI
        value: the text that will appear in the UI. note that since the key is not used to drive any display
            information, you need to include a name for the parameter in this value if you want it to be seen.
    """
    key: str
    value: str


class SuggestedQuestion(FrameworkBaseModel):
    """
    A question to suggest to the user as a followup. Appears in the chat UI under the most recent response.
    Attributes:
        label: the label of the question, this is the text that appears in the UI
        question: the actual question that is used as the next message in the chat thread if the user clicks on it.
            If not provided, the label will be used as-is.
    """
    label: str
    question: str | None = None


class SkillVisualization(FrameworkBaseModel):
    """

    Attributes:
        title: the title of the visualization, appears in places such as on the visualization's tab header when the
            visualizations are tabbed
        layout: a json-layout payload. see layouts.wire_layout for detail
    """
    title: str
    layout: str


class ExportData(FrameworkBaseModel):
    """
    Container class for data exports used to create spreadsheet downloads
    Attributes:
        name: A name to label the data. In a spreadsheet export, this becomes the title of the sheet.
        data: the raw data. this is a dataframe
    """
    name: str
    data: Any

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SkillOutput(FrameworkBaseModel):
    """
    Container for skill output
    Attributes:
        final_prompt: Used to prompt the model to generate the chat response
        narrative: A text element that can accompany the visualization. Markdown formatting supported.
        visualizations: One or more SkillVisualizations, consisting of a layout describing the visualization and associated metadata
        ppt_slides: One or more layout json strings, consisting of a layout describing the visualization and associated metadata for ppt export
        parameter_display_descriptions: A list of ParameterDisplayDescription objects that can be used to display information
            about the actual arguments that were used by the skill. Not limited to explicit skill parameters.
        followup_questions: A list of recommended followup questions for the user to ask.
            These will appear in the chat ui
        export_data: list of ExportData that will be made available as a spreadsheet download
    """
    final_prompt: str | None = None
    narrative: str | None = None
    visualizations: list[SkillVisualization] = Field(default_factory=list)
    ppt_slides: list[str] = Field(default_factory=list)
    pdfs: list[str] = Field(default_factory=list)
    parameter_display_descriptions: list[ParameterDisplayDescription] = Field(default_factory=list)
    followup_questions: list[SuggestedQuestion] = Field(default_factory=list)
    export_data: list[ExportData] = Field(default_factory=list)


class SkillConfig(FrameworkBaseModel):
    """
    this model class is used to generate the manifest when packaging a skill. anything added here
    will automatically be exported as part of that
    """
    name: str
    llm_name: str
    parameters: list[SkillParameter] = Field(default_factory=list)
    description: str | None = None
    parameter_guidance: str | None = None
    limitations: str | None = None
    capabilities: str | None = None
    example_questions: str | None = None


class Skill:
    def __init__(
            self,
            fn: Callable[[SkillInput], SkillOutput],
            config: SkillConfig,
    ):
        self.fn = fn
        self.config = config

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def create_input(self, assistant_id=None, arguments: dict | None = None) -> SkillInput:
        if not arguments:
            arguments = {}
        skill_arguments = _create_skill_arguments(self, arguments)
        return SkillInput(assistant_id=assistant_id, arguments=skill_arguments)


def _create_skill_arguments(skill: Skill, arguments):
    def field_type(p: SkillParameter):
        return list[Any] if p.is_multi else Any | None

    def parameter_field(p: SkillParameter):
        return Field(default=p.default_value) if not p.is_multi or p.default_value is not None else Field(default_factory=list)

    fields = {
        param.name: (field_type(param), parameter_field(param))
        for param in skill.config.parameters
    }
    cls = create_model(
        'SkillArguments',
        **fields,
    )
    valid_parameter_names = [param.name for param in skill.config.parameters]
    assign_args = {
        k: v for k, v in arguments.items() if k in valid_parameter_names
    }
    return cls(**assign_args)


@flexible_decorator
def skill(fn: Callable[[SkillInput], SkillOutput],
          name: str = None,
          parameters: list[SkillParameter] | None = None,
          description: str = None,
          llm_name: str | None = None,
          parameter_guidance: str | None = None,
          limitations: str | None = None,
          capabilities: str | None = None,
          example_questions: str | None = None,
    ):
    """
    Marks a function as a skill entry point.
    :param name: the name of the skill in the UI, will default to the function's name if not provided.
    :param llm_name: the name of the skill as it will be shown to the LLM. will default to the function's name if not provided.
    :param parameters: a list of SkillParameters
    :param description: the description of the skill for the LLM. this is used when selecting a skill to run.
    :param parameter_guidance: description of how to handle the skill's parameters. used in the system prompt passed to the LLM
    :param limitations: explanation of any limitations the skill has. used in the system prompt passed to the LLM
    :param capabilities: description of the skill's capabilities (ie what sort of questions it is good for answering).
        used in the system prompt passed to the llm
    :param example_questions: examples of questions that would be well-answered by this skill. used in the system prompt
        passed to the LLM
    :return: your skill function wrapped in a Skill class that wraps the metadata defined in the constructor and
        provides utility methods. This class defines __call__, so it can still be used like a normal function for the
        purposes of testing.
    """
    model = SkillConfig(
        name=name or fn.__name__,
        llm_name=llm_name or fn.__name__,
        parameters=parameters or [],
        description=description,
        parameter_guidance=parameter_guidance,
        capabilities=capabilities,
        limitations=limitations,
        example_questions=example_questions,
    )
    return Skill(fn, model)


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


class ExitFromSkillException(Exception):
    """
    Raise this exception to exit from your skill with a message that is used when creating the chat response to the user

    Attributes:
        message: the technical error message meant to aid in troubleshooting
        prompt_message: used when generating a chat response to the user. This can be used to
            do things like suggest the user provide additional information.
    """

    def __init__(self, message, prompt_message):
        super().__init__(message)
        self.message = message
        self.prompt_message = prompt_message
