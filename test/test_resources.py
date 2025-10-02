from skill_framework import skill_resource_path, copilot_resource_path, copilot_skill_resource_path


def test_local_path():
    path = skill_resource_path('test.txt')
    assert path == 'resources/test.txt'


def test_path_with_base(monkeypatch):
    monkeypatch.setenv('AR_SKILL_BASE_PATH', 'some_base_dir')
    path = skill_resource_path('test.txt')
    assert path == 'some_base_dir/resources/test.txt'


def test_copilot_skill_resource(monkeypatch):
    local_path = copilot_skill_resource_path('test.txt')
    assert local_path == 'resources/test.txt'
    monkeypatch.setenv('AR_COPILOT_SKILL_RESOURCE_PATH', 'some_base_dir')
    path = copilot_skill_resource_path('test.txt')
    assert path == 'some_base_dir/test.txt'
    nested_path = copilot_skill_resource_path('dir/test.txt')
    assert nested_path == 'some_base_dir/dir/test.txt'


def test_copilot_resource(monkeypatch):
    local_path = copilot_resource_path('test.txt')
    assert local_path == 'resources/test.txt'
    monkeypatch.setenv('AR_COPILOT_RESOURCE_PATH', 'some_base_dir')
    path = copilot_resource_path('test.txt')
    assert path == 'some_base_dir/test.txt'
    nested_path = copilot_resource_path('dir/test.txt')
    assert nested_path == 'some_base_dir/dir/test.txt'
