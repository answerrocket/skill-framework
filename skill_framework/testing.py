import os
from dotenv import dotenv_values

from skill_framework.skills import Skill
from skill_framework.preview import preview_skill


class SkillTestContext:
    """
    This is a context manager to make it simpler to test skills locally.
    """

    def __init__(self, skill, env_values: dict | None = None, env_file: str | None = None):
        """
        :param skill: the @skill-annotated function that this context will wrap
        :param env_values: values to set in the environment
        :param env_file: file from which to load environment variables
        """
        self.skill: Skill = skill
        self._initial_env = os.environ.copy()
        self._settings = _load_settings(env_values, env_file)

    def __enter__(self):
        for k, v in self._settings.items():
            if v:
                os.environ[k] = v
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ = self._initial_env

    def run(self, skill_args: dict):
        skill_input = self.skill.create_input(None, skill_args)
        return self.skill(skill_input)

    def preview_run(self, skill_args: dict):
        """
        Runs the skill with the provided arguments and writes preview files
        :param skill_args:
        :return:
        """
        output = self.run(skill_args)
        preview_skill(self.skill, output)
        return output


def _load_settings(env_values, env_file) -> dict:
    if not env_values:
        env_values = {}
    if not env_file:
        return env_values
    env_from_file = dotenv_values(env_file)
    return env_from_file | env_values

