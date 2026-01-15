import uuid
from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from enum import Enum
from logging import Logger

from pydantic import Field, ConfigDict, field_validator
from typing import List, Any, Callable, Optional, Literal

from skill_framework.common import FrameworkBaseModel
from skill_framework.diagnostics import Diagnostic

class PipelineStatusCode(Enum):
    unknown = "P000"

    # Success
    completed_full_results = "P101"
    # completed_partial_results = "P102"
    # completed_no_data = "P101"
    #
    # # Warnings/Refine
    # request_user_input = "P201"
    #
    # # Environment Errors
    # missing_skills = "P301"
    # missing_prompts = "P302"
    #
    # # Runtime Errors
    pipeline_runtime_error = "P401"
    pipeline_llm_call_failure = "P402"
    pipeline_sdk_call_failure = "P403"

    # Skill runtime errors
    skill_runtime_error = "S401"

class ContentBlock(FrameworkBaseModel):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    title: str
    layout_json: str
    type: Optional[Literal["INSIGHTS", "VISUAL"]] = "VISUAL"
    export_as_landscape: Optional[bool] = False

class ReportResult(FrameworkBaseModel):
    id: uuid.UUID
    answer_id: str
    title: str
    description: str
    report_name: str
    run_id: uuid.UUID
    parameters: Optional[List[Any]] = []
    content_blocks: Optional[List[ContentBlock]] = []
    slides: Optional[List[str]] = []
    has_slides: Optional[bool] = False
    pdfs: Optional[List[str]] = []
    has_pdfs: Optional[bool] = False
    cache_info: Optional[Any] = None
    progress_percent: Optional[int] = 100
    has_export_dataframes: Optional[bool] = False

class PipelineOutput(FrameworkBaseModel):
    report_results: Optional[List[ReportResult]] = []
    suggestions: Optional[List[str]] = []
    chat_messages: Optional[List[str]] = []
    status_message: Optional[str]
    status_code: Optional[PipelineStatusCode] = PipelineStatusCode.unknown

class EngineOutput(FrameworkBaseModel):
    status: str
    selectedPipelineName: str
    pipelineResult: PipelineOutput

class PipelineMetadata(FrameworkBaseModel):
    name: str
    description: str
    timeout_seconds: int = Field(default=timedelta(minutes=5).seconds)

# Anything that could be constructed by the Engine BEFORE the user sends a request
class PipelineContext(FrameworkBaseModel):
    tenant: str
    user_id: str
    copilot_id: str
    entry_id: str
    answer_id: str
    thread_id: str
    base_url: str
    llm_message_history: List[Any]

# Anything that must be constructed by the Engine AFTER the user sends a request
class PipelineRequest(FrameworkBaseModel):
    asked_at: datetime
    question: str

class AnswerEngineOutputTools(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def update_loading_message(self, message: str) -> None:
        """
        Updates the loading message shown to the user in the UI.
        :param message: The loading message to display.
        """
        pass

    @abstractmethod
    def stream_text(self, text: str) -> None:
        """
        Streams text output to the user in real-time. Each chunk of text sent will be added to the accumulating response buffer.
        :param text: The chunk of text to stream.
        """
        pass

    @abstractmethod
    def stream_skill_marker(self, answer_id: str):
        """
        Streams a skill marker to the user interface to indicate the start of a new skill's output.
        :param answer_id: The answer ID of the skill report result to mark.
        """
        pass

    @abstractmethod
    def get_report(self, report_id: str) -> ReportResult:
        """
        Gets a report associated with this answer by its ID
        :param report_id: The ID of the report to retrieve
        :return: ReportResult for the requested ID
        """
        pass

    @abstractmethod
    def add_report(self, report: ReportResult) -> None:
        """
        Adds a new report to the answer engine's output.
        :param report: The ReportResult to add.
        """
        pass

    @abstractmethod
    def update_report(self, report_id: str, updates: dict) -> ReportResult:
        """
        Updates an existing report with the specified fields.
        :param report_id: The ID of the report to update
        :param updates: A dictionary of fields to update on the report, only specified fields will be updated
        :return: The updated ReportResult
        """
        pass

    @abstractmethod
    def remove_report(self, report_id: str) -> None:
        """
        Removes a report from the answer engine's output by its ID.
        :param report_id: The ID of the report to remove.
        """
        pass


class ModelExecutionTarget(Enum):
    chat = "chat"
    narrative = "narrative"
    research = "research"

class ModelExecutionOptions(FrameworkBaseModel):
    should_stream_to_ui: bool = False
    """
    If True, the model output will be streamed back to the UI in real-time as it is generated.
    If False, the model output will be returned only after the model call is complete.
    """
    stream_callback: Optional[Callable[[str], None]] = None
    """
    A callback function that will be called with each chunk of text as it is generated by the model.
    """
    create_debug_entry: bool = False
    """
    If True, a debug entry will be created for this model execution in the diagnostics.
    """
    create_history_entries: bool = False
    """
    If True, the messages involved in this model execution will be added to the conversation history.
    """
    activity_tags: Optional[List[str]] = None
    """
    A list of activity tags to associate with this model execution for tracking and logging purposes.
    """

# FIXME better types for LLM messages
class AnswerEngineLlmTools(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_message_history(self) -> List[Any]:
        """
        Gets the current list of LLM messages in the conversation history.
        """
        pass

    @abstractmethod
    def add_message_to_history(self, message: Any) -> None:
        """
        Appends a new message to the end of the conversation history.
        :param message:
        """
        pass

    @abstractmethod
    def execute_chat(self, template: str, history: Optional[List[dict]] = None, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a chat model call with the specified template and history.
        :param template: A Jinja template string representing the prompt (will be populated with variables provided).
        :param history: A list of message dicts representing the conversation history.
        :param variables: A dict of variables to populate the template.
        :param options: ModelExecutionOptions to customize the execution.
        """
        pass

    @abstractmethod
    def execute_narrative(self, template: str, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a narrative model call with the specified template.
        :param template: A Jinja template string representing the prompt (will be populated with variables provided).
        :param variables: A dict of variables to populate the template.
        :param options: ModelExecutionOptions to customize the execution.
        """
        pass

    @abstractmethod
    def execute_research(self, template: str, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a research model call with the specified template.
        :param template: A Jinja template string representing the prompt (will be populated with variables provided).
        :param variables: A dict of variables to populate the template.
        :param options: ModelExecutionOptions to customize the execution.
        """
        pass

    @abstractmethod
    def execute_chat_for_prompt_name(self, prompt_name: str, history: Optional[List[dict]] = None, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a chat model call using a prompt identified by name.
        :param prompt_name: Relative name of the prompt to use (this is the name as specified in the prompt YAML file).
        :param history: A list of message dicts representing the conversation history.
        :param variables: A dict of variables to populate the prompt.
        :param options: ModelExecutionOptions to customize the execution.
        """
        pass

    @abstractmethod
    def execute_narrative_for_prompt_name(self, prompt_name: str, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a narrative model call using a prompt identified by name.
        :param prompt_name: Relative name of the prompt to use (this is the name as specified in the prompt YAML file).
        :param variables: A dict of variables to populate the prompt.
        :param options: ModelExecutionOptions to customize the execution.
        """
        pass

    @abstractmethod
    def execute_research_for_prompt_name(self, prompt_name: str, variables: Optional[dict] = None, options: Optional[ModelExecutionOptions] = None):
        """
        Executes a research model call using a prompt identified by name.
        :param prompt_name: Relative name of the prompt to use (this is the name as specified in the prompt YAML file).
        :param variables: A dict of variables to populate the prompt.
        :param options: ModelExecutionOptions to customize the execution.
        """

        pass

    @abstractmethod
    def get_prompt_by_name(self, prompt_name: str, variables: Optional[dict] = None):
        """
        Retrieves and hydrates a prompt by its name with the provided variables.
        :param prompt_name: Relative name of the prompt to retrieve (this is the name as specified in the prompt YAML file).
        :param variables: A dict of variables to populate the prompt.
        """
        pass

class ReportManager:
    """
    Used to modify the contents of a single ReportResult and relay the updates back to the
    answer engine.

    NOTE: currently NOT thread safe. Managing a single report from more than one thread at a time may have undefined behavior

    You should instantiate a ReportManager for each report you would like to manage.
    """

    def __init__(self, report_id: str, output_tools: AnswerEngineOutputTools):
        self.report_id = report_id
        self.tools = output_tools
        self.report = {}

    def get_report(self) -> ReportResult:
        """
        Gets the report result associated.
        :return: ReportResult
        """
        return self.tools.get_report(self.report_id)

    def update_report(self, updates: dict) -> ReportResult:
        """
        Updates the current report with the specified fields.
        :param updates: dictionary of fields to update on the report, only specified fields will be updated
        :return: updated ReportResult
        """
        return self.tools.update_report(self.report_id, updates)

    def add_content_block(self, new_block: ContentBlock):
        """
        Adds a new content block to the current report.
        :param new_block:
        :return:
        """
        current_report = self.get_report()
        self.tools.update_report(self.report_id, {"content_blocks": [*current_report.content_blocks, new_block]})

    def remove_content_block(self, block_id: str):
        """
        Removes a content block from the current report by ID.
        :param block_id:
        :return:
        """
        current_report = self.get_report()
        self.tools.update_report(self.report_id, {"content_blocks": [block for block in current_report.content_blocks if block.id != block_id]})

    def update_content_block(self, block_id: str, updates: dict):
        """
        Updates a content block in the current report by ID with the specified fields.
        :param block_id: id of the content block to update
        :param updates: dictionary of fields to update on the content block, only specified fields will be updated
        :return:
        """
        current_report = self.get_report()
        updated_blocks = []
        for block in current_report.content_blocks:
            if block.id == block_id:
                for key, value in updates.items():
                    setattr(block, key, value)
                updated_blocks.append(block)
            else:
                updated_blocks.append(block)
        self.tools.update_report(self.report_id, {"content_blocks": updated_blocks})


class AnswerEngineTools(FrameworkBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    add_diagnostic: Callable[[Diagnostic], None]
    logger: Logger
    pipeline_timer: Any
    outputs: AnswerEngineOutputTools
    llm: AnswerEngineLlmTools

    @classmethod
    @field_validator("outputs")
    def validate_output_tools(cls, val):
        if issubclass(type(val), AnswerEngineOutputTools):
            return val

        raise TypeError("outputs field must implement AnswerEngineOutputTools!")

    @classmethod
    @field_validator("outputs")
    def validate_llm_tools(cls, val):
        if issubclass(type(val), AnswerEngineLlmTools):
            return val

        raise TypeError("llm field must implement AnswerEngineLlmTools!")


class BasePipeline(ABC):

    @abstractmethod
    def __init__(self, pipeline_context: PipelineContext, answer_engine: AnswerEngineTools):
        pass

    @staticmethod
    @abstractmethod
    def get_pipeline_metadata() -> PipelineMetadata:
        """
        Returns data describing the current pipeline.
        """
        pass

    @abstractmethod
    def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
        """
        Main method to execute the pipeline logic. All operations before and including producing the output should be done here.

        For any operations that should be done after the output is sent to the UI, use `post_process_output`.

        :param request:
        :return: PipelineOutput the completed output of the pipeline
        """
        pass

    @abstractmethod
    def post_process_output(self, output: Optional[PipelineOutput]):
        """
        Method to be called after the pipeline has produced an output and sent it to the UI.

        This is useful for cleanup tasks that should not impact the user chat experience, such as logging, saving state,
        or sending emails/notifications.

        This method need not be implemented by all pipelines.
        """
        pass
