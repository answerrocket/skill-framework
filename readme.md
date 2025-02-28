This is a framework for creating AnswerRocket skills. It provides decorators
and utilities for turning your code into something that can be invoked by our platform.

# Install
`pip install skill-framework[ui]` to install the library with the local preview server

`pip install skill-framework` for a plain install

There are three command line utilities installed along with this library:

`package-skill <your_entry_file>.py` - packages your skill for upload to your AnswerRocket environment. This will generate a
manifest file from the `@skill`-annotated function in the file and then combine everything into a zip archive. This
utility will honor a .gitignore file if one is present in the project root.

`preview-server` - runs a local preview server to view rendered layouts locally.

`init-skill <skill_name>` to bootstrap a new skill. This will create the following:
```
.
├── .gitignore
├── resources/
├── .previews/
└── <skill_name>.py
```

`resources/` can be used for static resources that may be referenced by your layouts. The preview server can serve content
from this directory

`.previews/` is where generated preview layouts will be stored for viewing with the preview server

The `.gitignore` file will be pre-populated with entries common to python projects, along with the .preview directory.
If you already have one, this script will not replace it.

A skill needs to have a `@skill` decorated entry point, like this:

```python
from skill_framework import skill, SkillInput, SkillParameter, SkillOutput, SkillVisualization


@skill(
    name="my_skill",
    description="This is an example skill",
    parameters=[
        SkillParameter(
            name="dim",
            constrained_to="dimensions"
        )
    ]
)
def my_skill(parameters: SkillInput):
    # you can access arguments to your parameters extracted from
    # natural language queries via the arguments field
    # other run-specific context will also be provided on this object
    # everything here is just a mocked up example, you can form the parts of the response
    # in any way that makes sense for your skill.
    data = get_some_data(parameters)
    visualization = create_visualization(data)
    narrative = create_narrative(data)
    prompt = create_chat_response_prompt(data, narrative)
    return SkillOutput(
        final_prompt=prompt,
        narrative=narrative,
        visualizations=[visualization],
    )


def get_some_data(params):
    # use the client to get some data from a dataset
    pass


def create_visualization(data) -> SkillVisualization:
    # embed the data into a json layout payload
    pass


def create_narrative(data) -> str:
    # make some description of the data to appear as the narrative part of the response
    pass


def create_chat_response_prompt(data, narrative) -> str:
    # use the data and narrative to create a prompt for the model that will generate the response
    # in the chat window
    pass
```

You can generate a preview for viewing with the `preview-server` by passing your skill's output to `preview_skill`:

```python
from skill_framework import preview_skill, skill, SkillParameter

@skill(
    name="my skill",
    parameters=[
        SkillParameter(
            name="metric",
        )
    ]
)
def my_skill(skill_input):
    pass

if __name__ == '__main__':
    mock_input = my_skill.create_input(arguments={'metric': 'sales'})
    output = my_skill(mock_input)
    # this utility function will write the output to where the local preview server expects it
    preview_skill(my_skill, output)
```
