import os


def skill_resource_path(filename: str) -> str:
    """
    Helper for resolving the path of a resource file regardless of where the skill is running.
    """
    base_path = os.environ.get('AR_SKILL_BASE_PATH') or ''
    return os.path.join(base_path, 'resources', filename)


def copilot_skill_resource_path(filename: str) -> str:
    """
    Get the path to a copilot skill resource. When running locally, this will instead look in your skill resources/
    directory.
    :param filename: the file name including any directories it is nested in within the resource folder
    :return: the full path to the file for use with open() or other file reading utilities
    """
    resource_path = os.environ.get('AR_COPILOT_SKILL_RESOURCE_PATH')
    return os.path.join(resource_path, filename) if resource_path else skill_resource_path(filename)


def copilot_resource_path(filename: str) -> str:
    """
    Get the path to a copilot resource. When running locally, this will instead look in your skill resources/ directory.
    :param filename: the file name including any directories it is nested in within the resource folder
    :return: the full path to the file for use with open() or other file reading utilities
    """
    resource_path = os.environ.get('AR_COPILOT_RESOURCE_PATH')
    return os.path.join(resource_path, filename) if resource_path else skill_resource_path(filename)
