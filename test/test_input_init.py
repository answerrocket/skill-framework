from skill_framework import skill, SkillParameter, SkillInput

@skill(
    name="some_skill",
    parameters=[
        SkillParameter(name='metrics', is_multi=True),
        SkillParameter(name='dim')
    ]
)
def dummy_skill():
    pass


def test_args():
    skill_input: SkillInput = dummy_skill.create_input(arguments={'metrics': ['sales']})
    assert skill_input.arguments.metrics[0] == 'sales'
    assert skill_input.arguments.dim is None


def test_empty_args():
    skill_input = dummy_skill.create_input()
    assert isinstance(skill_input.arguments.metrics, list)
    assert len(skill_input.arguments.metrics) == 0
    assert skill_input.arguments.dim is None


def test_invalid_arg():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales'], 'bad_arg': 'some value'})
    assert skill_input.arguments.metrics[0] == 'sales'
    assert not hasattr(skill_input.arguments, 'bad_arg')


