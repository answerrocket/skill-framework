import json
from io import StringIO

from skill_framework import SkillVisualization
from skill_framework.preview import write_viz_preview


def test_preview_layout_is_json():
    viz = SkillVisualization(title="a visualization", layout='{"test": 1}')
    with StringIO() as file:
        write_viz_preview(file, viz)
        written = json.loads(file.getvalue())
        assert written['layout']['test'] == 1, 'layout should be embedded in preview file as real json'


def test_bad_layout_is_written():
    bad_viz = SkillVisualization(title="bad", layout="}")
    with StringIO() as file:
        write_viz_preview(file, bad_viz)
        written = file.getvalue()
        assert written == bad_viz.layout, 'should have written layout to file even if invalid'

