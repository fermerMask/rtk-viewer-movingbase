import plotly.graph_objs as go
import plotly.subplots as sp
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

from parser_test import parse_nmea

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
    <body>
        <h2>Upload NMEA (Motion + Map)</h2>
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

    # 🔥 完全版（6要素）
    lat, lon, speed, pitch, roll, heading = parse_nmea(lines)

    if len(lat) == 0:
        return """
        <html>
        <body>
            <h2>エラー: 有効な測位データがありません</h2>
            <a href="/">戻る</a>
        </body>
        </html>
        """

    # =========================
    # MAP
    # =========================
    fig_map = go.Figure()

    fig_map.add_trace(
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode="lines+markers",
            marker=dict(
                size=6,
                color=roll,  # 🔥 rollで色付け
                colorscale="RdBu",
                showscale=True,
                colorbar=dict(title="Roll (deg)"),
            ),
            name="trajectory",
        )
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=15,
        mapbox_center=dict(lat=lat[0], lon=lon[0]),
        height=600,
    )

    graph_map = fig_map.to_html(full_html=False)

    # =========================
    # 時系列グラフ
    # =========================
    fig = sp.make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("Speed", "Pitch / Roll", "Heading")
    )

    fig.add_trace(go.Scatter(y=speed, name="Speed"), row=1, col=1)

    fig.add_trace(go.Scatter(y=pitch, name="Pitch"), row=2, col=1)
    fig.add_trace(go.Scatter(y=roll, name="Roll"), row=2, col=1)

    fig.add_trace(go.Scatter(y=heading, name="Heading"), row=3, col=1)

    fig.update_layout(height=700)

    graph_motion = fig.to_html(full_html=False)

    # =========================
    # HTML
    # =========================
    return f"""
    <html>
    <body>
        <h2>Trajectory (Roll Colored)</h2>
        {graph_map}

        <h2>Motion Analysis</h2>
        {graph_motion}

        <br><a href="/">戻る</a>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)