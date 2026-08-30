# Pipelines

## Overview
Pipelines give you the ability to orchestrate complex workflows by combining multiple skills and language model calls into a single, cohesive process. They allow for structured execution of tasks, handling of intermediate results, and integration with user interfaces for real-time updates.

Pipelines can be uploaded or synced to a Max.ai assistant to be used in conversations or automated processes.

## Creating a Pipeline

To create a pipelines, extend the `BasePipeline` class and implement the necessary members.

This pipeline class will be the entry point to your pipeline.

```python
from skill_framework.pipelines import (
    BasePipeline,
    PipelineContext,
    PipelineMetadata,
    PipelineRequest,
    PipelineOutput,
    PipelineStatusCode,
    AnswerEngineTools,
)

class MyPipeline(BasePipeline):
    def __init__(self, pipeline_context: PipelineContext, answer_engine: AnswerEngineTools):
        self.context = pipeline_context
        self.engine = answer_engine
        self.logger = answer_engine.logger

    @staticmethod
    def get_pipeline_metadata() -> PipelineMetadata:
        return PipelineMetadata(
            name="my_pipeline",
            description="A pipeline that processes user questions",
            timeout_seconds=300,
        )

    def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
        self.logger.info(f"Processing question: {request.question}")

        # Your pipeline logic here

        return PipelineOutput(
            status_message="Pipeline completed successfully",
            status_code=PipelineStatusCode.completed_full_results,
        )

    def post_process_output(self, output: PipelineOutput):
        # Optional cleanup tasks (logging, notifications, etc.)
        self.logger.info("Post-processing complete")
```

## Dependencies
As well as the skill-framework package, the following packages are commonly used in pipelines and are supported by the AnswerRocket platform:

- answerrocket.client (PyPi) - for interacting with the AnswerRocket SDK
```python
from answer_rocket import AnswerRocketClient
```
- Pandas
- Pydantic
- numpy

Libraries other than those above (and the standard python library) will not be available in the AnswerRocket platform runtime environment and will result in an error.

## Best Practices

### Recommended File Organization
- Pipeline entry point should sit at the top level
- Place substeps into a `steps` folder
- Place prompts into a `prompts` folder
- Place visual layout templates into a `layouts` folder

#### Example directory structure:
```
my_pipeline/
├── __init__.py
├── pipelines.txt       
├── pipeline.py              # Main pipeline class (entry point)
├── steps/
│   ├── __init__.py
│   ├── data_retrieval.py
│   ├── analysis.py
│   └── report_generation.py
├── prompts/
│   ├── analysis_prompt.yaml
│   └── summary_prompt.yaml
└── layouts/
    ├── chart_layout.json
    └── table_layout.json
```

### Leveraging Engine Tools
Leverage the built-in engine tools as much as possible to simplify common tasks and ensure compatibility with the AnswerRocket platform.

#### Create class members for commonly used tools and context on your pipeline instance

Initializing needed tools and fields on your pipeline class reduces boilerplate in your pipeline methods.

This is not strictly required, but can improve readability.

```python
def __init__(self, pipeline_context, answer_engine):
    self.thread_id = pipeline_context.thread_id
    self.entry_id = pipeline_context.entry_id
    self.answer_id = pipeline_context.answer_id
    self.user_id = pipeline_context.user_id
    self.base_url = pipeline_context.base_url
    self.client = AnswerRocketClient()
    self.tools = answer_engine
    self.logger = self.tools.logger
    self.timer = self.tools.pipeline_timer
    self.chat_history = pipeline_context.llm_message_history
    self.output_tools = answer_engine.outputs

```

### Updating the UI
#### Send frequent status messages to the UI to indicate progress
#### Send intermediate report results to the UI as soon as meaningful visual outputs are available
#### Stream text that you want to appear as a chat message in the UI

```python
def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    outputs = self.engine.outputs

    # Update the loading indicator with status messages
    outputs.update_loading_message("Analyzing your question...")

    # Perform some analysis step
    analysis_result = self.analyze(request.question)

    outputs.update_loading_message("Generating insights...")

    # Stream text directly to the chat UI
    outputs.stream_text("Based on my analysis, ")
    outputs.stream_text("here are the key findings:\n\n")

    # Add a report result with visual content
    report = ReportResult(
        id=uuid.uuid4(),
        answer_id=self.context.answer_id,
        title="Analysis Results",
        description="Summary of the analysis",
        report_name="analysis_report",
        run_id=uuid.uuid4(),
        content_blocks=[
            ContentBlock(
                title="Chart",
                layout_json=json.dumps(chart_data),
            )
        ],
    )
    outputs.add_report(report)

    # Mark the end of streaming
    outputs.mark_stream_complete()

    return PipelineOutput(
        status_code=PipelineStatusCode.completed_full_results,
    )
```

### Leveraging the SDK
The AnswerRocket client (also refered to as the Max SDK) provides a variety of helper methods and classes to simplify common tasks in pipelines.

View the GitHub repository for the SDK to explore all available functionality: https://github.com/answerrocket/answerrocket-python-client

Here are some common use-cases for the SDK in pipelines:
- retrieve information about the current user and assistant (copilot)
- ask new questions to the chat pipeline
- execute skills (sync or async)
- retrieve datasets, dimensions, and metrics

### Logging and Monitoring
#### Log important events
Leverage the built-in logger in the engine tools to log all important information.

Use an appropriate logging level (e.g., INFO, WARNING, ERROR) to log significant events in the pipeline execution. This includes the start and end of major steps, any errors encountered, and key decision points.

When logging a caught exception, include the stack trace to aid in debugging.

```python
def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    logger = self.engine.logger

    logger.info(f"Starting pipeline for question: {request.question}")

    try:
        result = self.perform_analysis()
        logger.info(f"Analysis completed with {len(result)} records")
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise

    logger.warning("Data quality issues detected in source")

    return PipelineOutput(status_code=PipelineStatusCode.completed_full_results)
```

#### Capture performance metrics using the timer context

```python

...

def __init__(self, pipeline_context, answer_engine):
    self.timer = self.tools.pipeline_timer

def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    
    with self.timer("data_retrieval"):
        data = self.fetch_data()

    with self.timer("analysis"):
        results = self.analyze(data)

    with self.timer("report_generation"):
        report = self.generate_report(results)

    # Timer metrics are automatically captured and available in diagnostics
    return PipelineOutput(status_code=PipelineStatusCode.completed_full_results)
```

#### Use the diagnostics tool for more complex debugging data
When logs are not sufficient or would be difficult to interpret or sift through for an important piece of diagnostic data, consider using the diagnostics tool to capture more complex debugging data. This can include snapshots of the pipeline state, variable values, and execution flow at specific points in time.
Diagnostics data has the advantage of being displayed in the UI with better readability.

```python
from skill_framework.diagnostics import Diagnostic, DiagnosticItem

def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    # Add diagnostic data for debugging
    self.engine.add_diagnostic(Diagnostic(
        title="Input Parameters",
        type="pipeline_debug",
        items=[
            DiagnosticItem(
                title="Request Details",
                json={
                    "question": request.question,
                    "user_id": self.context.user_id,
                    "timestamp": request.asked_at.isoformat(),
                },
            )
        ],
    ))

    intermediate_state = self.process_step_one()

    self.engine.add_diagnostic(Diagnostic(
        title="Step One Output",
        type="pipeline_debug",
        items=[
            DiagnosticItem(
                title="Intermediate State",
                json=intermediate_state,
            )
        ],
    ))

    # ...
```

### Using Prompts and Making Model Calls
#### Use LLM tools to call the appropriate target model
- chat - for conversational interactions that involve a chat history
- narrative - for generating long-form text responses
- research - for deep-reasoning tasks that require retrieval and synthesis of information

```python
from skill_framework.pipelines import ModelExecutionOptions

def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    llm = self.engine.llm

    # Simple chat call with inline template
    chat_response = llm.execute_chat(
        template="You are a helpful assistant. Answer: {{question}}",
        variables={"question": request.question},
    )

    # Narrative call for long-form content
    narrative_response = llm.execute_narrative(
        template="Write a detailed analysis of the following topic:\n\n{{topic}}",
        variables={"topic": "market trends"},
    )

    # Research call for complex reasoning
    research_response = llm.execute_research(
        template="Research and synthesize information about {{subject}}",
        variables={"subject": "renewable energy adoption"},
    )

    # Stream response directly to UI
    llm.execute_chat(
        template="Explain {{concept}} in simple terms.",
        variables={"concept": "machine learning"},
        options=ModelExecutionOptions(should_stream_to_ui=True),
    )

    # Use a custom callback to process streamed chunks
    def on_chunk(chunk: str):
        print(f"Received: {chunk}")

    llm.execute_narrative(
        template="Generate a summary of {{data}}",
        variables={"data": "quarterly sales"},
        options=ModelExecutionOptions(stream_callback=on_chunk),
    )

    # ...
```

#### Define your core prompts in a `prompts` folder
For each core prompt you want your pipeline to reference, create a prompt_name.yaml file where prompt_name is a descriptive name for the prompt.
Store these files in a `prompts` folder within your pipeline's directory structure.

Whenever possible, write and leverage your prompts in the `prompts` folder. Using prompt YAML files allows
the Max platform to provide useful instrumentation, versioning, and override features from the UI or SDK.

If prompt's require dynamic content, use the `variables` section of the prompt YAML to define placeholders that can be filled in at runtime.

Reference the core-prompt.schema.json in the `schemas` folder to understand the structure and required fields for defining prompts.

**Example prompt YAML file (`prompts/analysis_prompt.yaml`):**

```yaml
meta:
  name: analysis_prompt
  description: Generates an analysis of the provided data with key insights.

template: |
  Analyze the following data and provide key insights:

  <data>
  {{data}}
  </data>

  Focus on:
  - Trends and patterns
  - Anomalies or outliers
  - Actionable recommendations

auxiliaryTemplate: |
  You are a data analyst specializing in {{domain}}.
  Provide clear, concise insights backed by the data.
```

#### Execute prompts by name

The preferred way to manage and execute prompts is to define them in YAML files and reference them by name in your pipeline code.
While calling prompts inline is supported via the `execute_narrative`, `execute_chat`, and `execute_research` methods, using named prompts provides better maintainability and leverages platform features.

```python
def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    llm = self.engine.llm

    # Execute a prompt defined in a YAML file by name
    response = llm.execute_narrative_for_prompt_name(
        prompt_name="analysis_prompt",
        variables={
            "data": formatted_data,
            "domain": "sales analytics",
        },
    )

    # Chat with history using a named prompt
    history = llm.get_message_history()
    chat_response = llm.execute_chat_for_prompt_name(
        prompt_name="conversational_assistant",
        history=history,
        variables={"user_name": "John"},
    )

    # Add the response to conversation history
    llm.add_message_to_history({"role": "assistant", "content": chat_response})

    # Retrieve a hydrated prompt without executing it
    hydrated_prompt = llm.get_prompt_by_name(
        prompt_name="analysis_prompt",
        variables={"data": "sample data", "domain": "finance"},
    )

    # ...
```

### Error Handling

```python
from skill_framework.pipelines import PipelineStatusCode

def execute_pipeline(self, request: PipelineRequest) -> PipelineOutput:
    logger = self.engine.logger
    outputs = self.engine.outputs

    try:
        outputs.update_loading_message("Processing your request...")
        result = self.perform_risky_operation()

    except ConnectionError as e:
        logger.error(f"SDK connection failed: {e}", exc_info=True)
        return PipelineOutput(
            status_message="Unable to connect to required services. Please try again.",
            status_code=PipelineStatusCode.pipeline_sdk_call_failure,
        )

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        return PipelineOutput(
            status_message=f"Invalid input provided: {e}",
            status_code=PipelineStatusCode.pipeline_runtime_error,
        )

    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        return PipelineOutput(
            status_message="An unexpected error occurred. Please contact support.",
            status_code=PipelineStatusCode.pipeline_runtime_error,
        )

    return PipelineOutput(
        status_message="Success",
        status_code=PipelineStatusCode.completed_full_results,
    )


def call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
    """Example of handling LLM call failures with retry logic."""
    logger = self.engine.logger

    for attempt in range(max_retries):
        try:
            return self.engine.llm.execute_narrative(template=prompt)
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All LLM retry attempts exhausted", exc_info=True)
                raise
    return ""
```
### Annotating Dataframes

It is common for pipelines that perform data analysis to produce pandas DataFrames as part of their output.
When doing so, it is recommended to annotate these DataFrames with metadata to provide additional context about the data using max_metadata field on any Pandas DataFrame.

```python
my_df.max_metadata.set_description("Sales data for Q1 2024 broken out by brand.")
```

### Producing Visual Outputs

#### Break outputs into separate content blocks when appropriate
Each report result can contain multiple content blocks. On the Max UX, each content block will be
rendered as a separate named tab. This is a useful way to break up large reports into sections that a user can easily navigate between.

Examples of content you may want to separate into different content blocks include:
- status pages vs main content
- discrete or unrelated analyses
- multiple attempts of the same analysis with different parameters

#### Break reports into multiple report results if appropriate
In most cases, your pipeline will only need to produce a single report result. However, there are scenarios where it may be beneficial to break up a large report into multiple report results.

Each report result will be rendered as a separate clickable box in the chat conversation. Each report result manages its own set of exportable data and group of tabs (content blocks).

Use cases where you may want to break up a pipeline output into multiple report results include:
- distinct analyses that a user may want to explore/export separately
- results that cannot be easily or coherently combined into a single report
- instances where you want to emphasize the individual skills or steps executed to produce each report result

#### Leverage the dynamic layouts system to create rich visual outputs
All content block outputs are expected to abide by the AnswerRocket layout JSON format.
As stated in the above section on filesystem structure, these are best placed in a `layouts` folder within your pipeline's directory structure.

To understand the layout JSON format, inspect the dynamic layouts yarn package (`"@answerrocket/dynamic-layout": "bitbucket:aglabs/dynamic-layout#main"`). There are example layouts and schema files to help you better understand how to construct valid layout JSON.

The dynamic layout structure allows for variable substitutions. It is advised you take advantage of this system when possible.
For more complex use-cases such as lists, conditional content, or loops you may alternatively decide to use Jinja templating,
construct your layouts with string operations programmatically, or some combination of the two.

#### Link your dataframes back to charts and tables
When producing visual outputs that are based on dataframes, it is recommended to link the dataframe back to the visual elements in your layout JSON.

While this is not strictly required, it allows for easier tracking and verification of visualization data. This can be used to inform better
report generation, data exports, and fact-checking.

To do this, include a `_meta_sourceDataframeId` on your chart or table component.

```json
{
  "type": "chart",
  "title": "Sales Over Time",
  "data": {
    "_meta_sourceDataframeId": {{chart_dataframe_id}},
    "x": "date",
    "y": "sales"
  }
}
```

You will likely then need to use the `my_df.max_metadata.get_id()` to retrieve the dataframe ID to substitute into your layout JSON.

NOTE: the answerrocket python client must be imported in your project to utilize the max_metadata functionality on pandas DataFrames.

### Extra Notes
Here are a few extra notes and tips for working with pipelines:
- Currently the platform only knows how to pick up prompts in a folder called `prompts`. Other folder names will not be recognized.
This folder must live on the same level as the python file that you will be running the package command against to be recognized.
- When using the `package-skill` command, make sure to run it from the same level that your pipeline entry point file lives in.
- While you may use a requirements.txt for development purposes, the AnswerRocket platform will not install any dependencies beyond those listed in the "Dependencies" section above.
- You should include a pipelines.txt file that points to your pipeline's entry point file (in most cases just a single line with the file name)

### Pitfalls to Avoid
#### Avoid infinite loops

```python
# BAD: Potential infinite loop
def process_until_done(self):
    while True:
        result = self.check_status()
        if result == "done":
            break

# GOOD: Use a maximum iteration count
def process_until_done(self):
    max_iterations = 100
    for i in range(max_iterations):
        result = self.check_status()
        if result == "done":
            return result
        self.engine.logger.debug(f"Iteration {i}: status = {result}")
    raise RuntimeError(f"Processing did not complete within {max_iterations} iterations")
```

#### Avoid catching errors without proper logging

```python
# BAD: Silently swallowing errors
try:
    result = self.risky_operation()
except Exception:
    pass  # Error is lost forever

# GOOD: Log errors before handling
try:
    result = self.risky_operation()
except Exception as e:
    self.engine.logger.error(f"Operation failed: {e}", exc_info=True)
    # Re-raise, return error response, or handle appropriately
    raise
```

#### Avoid excessive comments

Pipeline code should be self-documenting through clear naming conventions and modular structure.

Comments should only be used to explain non-obvious logic or decisions that are not immediately clear from the code itself.

If it is not clear what a function does by its name, it should probably be broken up into smaller functions with descriptive names and adequate docs.

