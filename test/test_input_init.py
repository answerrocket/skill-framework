from skill_framework import skill, SkillParameter, SkillInput

@skill(
    name="some_skill",
    parameters=[
        SkillParameter(name='metrics', is_multi=True),
        SkillParameter(name='dim'),
        SkillParameter(name='another_dim', default_value="state"),
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
    assert skill_input.arguments.another_dim == 'state'


def test_invalid_arg():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales'], 'bad_arg': 'some value'})
    assert skill_input.arguments.metrics[0] == 'sales'
    assert not hasattr(skill_input.arguments, 'bad_arg')


def test_request_source_defaults_web():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']})
    assert skill_input.request_source == 'WEB'


def test_request_source_passthrough():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='MOBILE')
    assert skill_input.request_source == 'MOBILE'


def test_request_source_is_not_a_declared_argument():
    # request_source is request context surfaced on SkillInput, never a declared skill parameter
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='MOBILE')
    assert not hasattr(skill_input.arguments, 'request_source')


