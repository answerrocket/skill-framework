from skill_framework.layouts import wire_layout
import json

layout = """
{
    "layoutJson": {
        "type": "Document",
        "rows": 90,
        "columns": 160,
        "rowHeight": "1.11%",
        "colWidth": "0.625%",
        "gap": "0px",
        "style": {
            "backgroundColor": "#ffffff",
            "width": "100%",
            "height": "max-content"
        },
        "children": [
            {
                "name": "Header0",
                "type": "Header",
                "children": "",
                "text": "Enter Header Text",
                "style": {
                    "fontSize": "20px",
                    "fontWeight": "normal"
                }
            }
        ]
    },
    "inputVariables": [
        {
            "name": "text",
            "isRequired": false,
            "defaultValue": null,
            "targets": [
                {
                    "elementName": "Header0",
                    "fieldName": "text"
                }
            ]
        }
    ]
}
"""


def test_layout_wire():
    layout_json = json.loads(layout)
    inputs = {'text': "the header"}
    wired = wire_layout(layout_json, inputs)
    completed_layout = json.loads(wired)
    header_element = completed_layout.get('children')[0]
    assert header_element['text'] == 'the header'
