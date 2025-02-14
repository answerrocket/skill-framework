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
    output_id = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    path = f'.previews/{skill.fn.__name__}'
    if not os.path.exists(f'{path}'):
        os.makedirs(f'{path}', exist_ok=True)
    with open(f'{path}/{output_id}.json', 'w') as f:
        f.write(skill_output.visualization)
        print(f'run preview-server and go to localhost:8484/print/{skill.fn.__name__}/{output_id}')
