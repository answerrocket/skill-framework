from skill_framework import skill, SkillParameter, SkillInput, RequestSource

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
    assert skill_input.request_source is RequestSource.WEB


def test_request_source_parses_string_to_enum():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='MOBILE')
    assert skill_input.request_source is RequestSource.MOBILE


def test_request_source_accepts_enum():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source=RequestSource.MOBILE)
    assert skill_input.request_source is RequestSource.MOBILE


def test_request_source_is_case_insensitive():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='mobile')
    assert skill_input.request_source is RequestSource.MOBILE


def test_request_source_unknown_falls_back_to_web():
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='future_source')
    assert skill_input.request_source is RequestSource.WEB


def test_request_source_is_not_a_declared_argument():
    # request_source is request context surfaced on SkillInput, never a declared skill parameter
    skill_input = dummy_skill.create_input(arguments={'metrics': ['sales']}, request_source='MOBILE')
    assert not hasattr(skill_input.arguments, 'request_source')


