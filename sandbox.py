import plotly.graph_objs as go
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

from parser_test import parse_rmc

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
    <body>
        <h2>Upload NMEA (Map Test)</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input name="file" type="file">
            <input type="submit">
        </form>
    </body>
    </html>
    """


@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode().splitlines()

    lat, lon, speed = parse_rmc(lines)

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode="lines+markers",
            marker=dict(
                size=5,
                color=speed,
                colorscale="Jet",
                showscale=True,
                colorbar=dict(title="Speed(m/s)"),
            ),
            name="trajectory",
        )
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=15,
        mapbox_center=dict(lat=lat[0], lon=lon[0]),
        height=700,
    )

    graph_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <body>
        <h2>Trajectory Test</h2>
        {graph_html}
        <br><a href="/">戻る</a>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
