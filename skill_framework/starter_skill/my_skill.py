from skill_framework import skill, SkillParameter, SkillInput, SkillOutput


@skill(
    name="my_skill",
    description="An example skill",
    parameters=[
        SkillParameter(
            name="metric",
            constrained_to="metrics",
        )
    ]
)
def my_skill(parameters: SkillInput) -> SkillOutput:
    pass
