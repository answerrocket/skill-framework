import os

from skill_framework.testing import SkillTestContext
from skill_framework import skill, SkillParameter, SkillOutput


@skill(
    name="test",
    parameters=[
        SkillParameter(name="a")
    ]
)
def harness_tester(skill_input):
    some_value = os.getenv('SOME_VALUE')
    prompt = f'{some_value} - {skill_input.arguments.a}'
    return SkillOutput(final_prompt=prompt)


def test_harness():
    with SkillTestContext(harness_tester, {'SOME_VALUE': 'test'}) as ctx:
        output = ctx.run({'a': 'an argument'})
        assert output.final_prompt == 'test - an argument'


def test_harness_file():
    env_path = os.path.join(os.path.dirname(__file__), 'test.env')
    with SkillTestContext(harness_tester, env_file=env_path) as ctx:
        output = ctx.run({'a': 'an argument'})
    assert output.final_prompt == 'value - an argument'


def test_harness_file_override():
    env_path = os.path.join(os.path.dirname(__file__), 'test.env')
    with SkillTestContext(harness_tester, env_values={'SOME_VALUE': 'test'}, env_file=env_path) as ctx:
        output = ctx.run({'a': 'an argument'})
    assert output.final_prompt == 'test - an argument'
