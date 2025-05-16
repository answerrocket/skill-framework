from skill_framework import skill_resource_path


def test_local_path():
    path = skill_resource_path('test.txt')
    assert path == 'resources/test.txt'


def test_path_with_base(monkeypatch):
    monkeypatch.setenv('AR_SKILL_BASE_PATH', 'some_base_dir')
    path = skill_resource_path('test.txt')
    assert path == 'some_base_dir/resources/test.txt'

