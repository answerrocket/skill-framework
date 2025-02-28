import json
import os

from skill_framework import SkillOutput, SkillVisualization


def preview_skill(skill, skill_output: SkillOutput):
    """
    Writes skill template output to a file so that it can be seen by the preview app
    :param skill: the skill function
    :param skill_output: the output of the skill
    """
    path = f'.previews/{skill.fn.__name__}'
    if not os.path.exists(f'{path}'):
        os.makedirs(f'{path}', exist_ok=True)
    for idx, viz in enumerate(skill_output.visualizations):
        with open(f'{path}/viz-{idx}.json', 'w') as f:
            write_viz_preview(f, viz)

    print(f'Preview at localhost:8484/print/{skill.fn.__name__}')


def write_viz_preview(file, viz: SkillVisualization):
    # this is not just calling model_dump_json so that the json embedded in the layout can be written out
    # as json that can be read by a human, since this is for previewing outputs.
    try:
        viz_dict = viz.model_dump()
        viz_dict['layout'] = json.loads(viz_dict['layout'])
        file.write(json.dumps(viz_dict, indent=2))
    except Exception:
        # write it out even if invalid so the user can still review it, the preview server skips invalid layouts
        print(f'{viz.title} contains invalid json')
        file.write(viz.layout)
