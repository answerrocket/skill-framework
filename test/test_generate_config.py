import os
import shutil

from skill_framework.package import _generate_config


def test_starter_skill_config(monkeypatch, tmp_path):
    shutil.copy(os.path.join('skill_framework', 'starter_skill', 'my_skill.py'), tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend('')
    config = _generate_config('my_skill.py')
    assert config['entry_file'] == 'my_skill.py'
    assert config['entry_point'] == 'my_skill'
