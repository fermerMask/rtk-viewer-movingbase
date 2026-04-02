from cgi import parse

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

from parser import parse_hrp

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>RTK Viewer</title>
        </head>
        <body>
            <h1>RTK Viewer</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input name="file" type="file">
                <input type="submit">
            </form>
        </body>
    </html>
    """


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode().splitlines()

    data = parse_hrp(lines)
