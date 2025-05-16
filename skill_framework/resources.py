import os


def skill_resource_path(filename: str):
    """
    Helper for resolving the path of a resource file regardless of where the skill is running.
    """
    base_path = os.environ.get('AR_SKILL_BASE_PATH') or ''
    return os.path.join(base_path, 'resources', filename)
