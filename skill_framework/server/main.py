import json
import logging

import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger("uvicorn.error")


app = FastAPI()

app.mount("/resources", StaticFiles(directory="resources"), name="resources")


@app.get("/previews/{rest_of_path:path}")
def get_layout(rest_of_path: str):
    layouts = []
    for dirpath, _, filenames in os.walk(os.path.join('.previews', rest_of_path)):
        for filename in filenames:
            if not filename.endswith('.json'):
                continue
            with open(os.path.join('.previews', rest_of_path, filename), 'r') as f:
                try:
                    layout = json.load(f)
                    layouts.append(layout)
                except Exception:
                    logger.error(f"failed to load layout from {filename}")
    return layouts


app.mount("/static", StaticFiles(directory=f"{os.path.join(os.path.dirname(__file__), 'ui/static')}"), name='ui')

templates = Jinja2Templates(directory=f"{os.path.join(os.path.dirname(__file__), 'ui')}")


@app.get("/{rest_of_path:path}")
async def react_app(req: Request):
    return templates.TemplateResponse(name='index.html', request=req)


def run():
    uvicorn.run("skill_framework.server.main:app", port=8484, reload=True, log_level='info')
