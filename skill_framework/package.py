import importlib
import json
import keyword
import os
import pathspec
import shutil
import sys
import zipfile
from pprint import pprint
from skill_framework.skills import Skill


def package_skill():
    import argparse
    parser = argparse.ArgumentParser(description='packages skills')
    parser.add_argument('entry_file', type=str)
    sys.path.append('')
    args = parser.parse_args()
    _package_skill(args.entry_file)


def _package_skill(entry_file):
    entry_mod_name = entry_file.split('.py')[0]
    skill_config = _generate_config(entry_file)
    skill_files = _discover_files()
    pprint(skill_config)
    with zipfile.ZipFile(f'{entry_mod_name}.zip', mode='w') as zip:
        print('packaging skill...')
        zip.writestr('skill_config.json', json.dumps(skill_config, indent=2))
        for file in skill_files:
            if file == f'{entry_mod_name}.zip':
                continue
            print(f'including {file}')
            zip.write(file)
        print(f'created {entry_mod_name}.zip')


def _discover_files():
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as gitignore:
            spec = pathspec.GitIgnoreSpec.from_lines(gitignore.readlines())
            return spec.match_tree('.', negate=True)
    skill_files = []
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            skill_files.append(os.path.join(dirpath, filename))
    return skill_files


def init_skill():
    import argparse
    parser = argparse.ArgumentParser(description='initializes a skill')
    parser.add_argument('skill_name', type=str)
    args = parser.parse_args()
    _init_skill(args.skill_name)


def _init_skill(skill_name="my_skill"):
    if not skill_name.isidentifier() or keyword.iskeyword(skill_name):
        raise Exception(f"Invalid skill name: {skill_name}. Skill name should be a valid python identifier")
    os.makedirs("resources", exist_ok=True)
    with (open(f'{skill_name}.py', 'w') as new_skill,
          open(os.path.join(os.path.dirname(__file__), 'starter_skill', 'my_skill.py')) as template):
        template_content = template.read()
        completed_template = template_content.replace('my_skill', skill_name)
        new_skill.write(completed_template)
    if not os.path.exists('.gitignore'):
        shutil.copy(os.path.join(os.path.dirname(__file__), 'starter_skill', '.gitignore'), '.')


def _generate_config(entry_file):
    entry_file_base = os.path.basename(entry_file)
    entry_mod_name = entry_file_base.split('.py')[0]
    entry_mod = importlib.import_module(entry_mod_name)
    skill = next((attr for attr_name, attr in entry_mod.__dict__.items() if isinstance(attr, Skill)), None)
    if not isinstance(skill, Skill):
        raise Exception(f"Could not find a function with @skill annotation in {entry_file_base}")
    return {
        'name': skill.name,
        'description': skill.description,
        'detailed_description': skill.description,
        'parameters': [p.model_dump() for p in skill.parameters],
        'entry_file': entry_file_base,
        'entry_point': skill.fn.__name__,
    }
