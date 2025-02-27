import os.path
import datetime

from skill_framework import SkillOutput


def preview_skill(skill, skill_output: SkillOutput):
    """
    Writes skill template output to a file so that it can be seen by the preview app
    :param skill: the skill function
    :param skill_output: the output of the skill
    :return:
    """
    path = f'.previews/{skill.fn.__name__}'
    if not os.path.exists(f'{path}'):
        os.makedirs(f'{path}', exist_ok=True)
    for idx, viz in enumerate(skill_output.visualizations):
        with open(f'{path}/viz-{idx}.json', 'w') as f:
            f.write(viz.model_dump_json())
    print(f'Preview at localhost:8484/print/{skill.fn.__name__}')
