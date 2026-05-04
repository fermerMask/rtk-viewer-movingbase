import datetime
import io
import math
import os
import subprocess
import sys
import threading

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from pyproj import Transformer


class NMEA:
    mode = {0: "NA", 1: "Standalone", 2: "DGNSS", 4: "RTK Fixed", 5: "RTK Float"}

    @classmethod
    def hms_to_sec(cls, hms):
        d = [int(c) for c in hms if c != "."]
        h = d[0] * 10 + d[1] + 9
        m = d[2] * 10 + d[3]
        s = d[4] * 10 + d[5] + d[6] * 0.1 + d[7] * 0.01
        t = h * 3600 + m * 60 + s
        return t

    @classmethod
    def dm_to_sd(cls, dm):
        x = float(dm)
        d = x // 100
        m = (x - d * 100) / 60
        return d + m

    @classmethod
    def knot_to_meters(cls, knot):
        return float(knot) * 1852 / 3600

    @classmethod
    def parse_GGA(cls, line):
        ds = line.strip().split(",")
        if (
            ds[0][3:6] == "GGA"
            and ds[1] != ""
            and ds[2] != ""
            and ds[4] != ""
            and ds[6] != ""
            and ds[9] != ""
        ):
            try:
                t = NMEA.hms_to_sec(ds[1])
                lat = NMEA.dm_to_sd(ds[2])
                lon = NMEA.dm_to_sd(ds[4])
                mode = int(ds[6])
                alt = float(ds[9])
                return t, lat, lon, mode, alt

            except:
                return None

    @classmethod
    def parse_RMC(cls, line):
        ds = line.strip().split(",")
        if ds[0][3:6] == "RMC" and ds[3] != "" and ds[5] != "" and ds[7] != "":
            try:
                t = NMEA.hms_to_sec(ds[1])
                lat = NMEA.dm_to_sd(ds[3])
                lon = NMEA.dm_to_sd(ds[5])
                vel = NMEA.knot_to_meters(ds[7])

                return t, lat, lon, vel
            except (ValueError, IndexError):
                return None

    @classmethod
    def parse_PSSN_HRP(cls, line):
        ds = line.strip().split(",")

        if (
            len(ds) > 12
            and ds[0].startswith("$PSSN")
            and ds[1] == "HRP"
            and ds[2] != ""
        ):
            try:
                t = NMEA.hms_to_sec(ds[2])
                heading = float(ds[4]) if ds[4] != "" else None
                roll = float(ds[5]) if ds[5] != "" else None
                pitch = float(ds[6]) if ds[6] != "" else None

                heading_std = float(ds[7]) if ds[7] != "" else None
                roll_std = float(ds[8]) if ds[8] != "" else None
                pitch_std = float(ds[9]) if ds[9] != "" else None

                quality = int(ds[11]) if ds[11] != "" else None
                # print(quality)

                return (
                    t,
                    heading,
                    roll,
                    pitch,
                    heading_std,
                    roll_std,
                    pitch_std,
                    quality,
                )

            except (ValueError, IndexError):
                return None
        else:
            return None

    def load(self, fn):
        self.lines = open(fn).readlines()
        dict = {}

        for line in self.lines:
            r = NMEA.parse_GGA(line)
            if r is not None:
                t, lat, lon, mode, alt = r
                if t not in dict:
                    dict[t] = {}
                dict[t]["lat"] = lat
                dict[t]["lon"] = lon
                dict[t]["mode"] = mode
                dict[t]["alt"] = alt
                continue

            r = NMEA.parse_RMC(line)
            if r is not None:
                t, lat, lon, vel = r
                if t not in dict:
                    dict[t] = {}

                dict[t]["lat"] = lat
                dict[t]["lon"] = lon
                dict[t]["vel"] = vel
                continue

            r = NMEA.parse_PSSN_HRP(line)
            if r is not None:
                t, heading, roll, pitch, heading_std, roll_std, pitch_std, quality = r
                if t not in dict:
                    dict[t] = {}

                dict[t]["heading"] = heading
                dict[t]["roll"] = roll
                dict[t]["pitch"] = pitch
                dict[t]["heading_std"] = heading_std
                dict[t]["roll_std"] = roll_std
                dict[t]["pitch_std"] = pitch_std
                dict[t]["quality"] = quality

                continue

        self.dict = dict
        print("[INFO]loading File")

        return dict

    def get_data(self, t1=-1, t2=-1):
        print("[INFO] extract all data...")
        dict = self.dict

        ts = sorted(dict.keys())

        xs, ys, zs = [], [], []
        vs, modes = [], []
        lats, lons = [], []
        headings, headings_std = [], []
        rolls, rolls_std = [], []
        pitchs, pitchs_std = [], []
        qualities = []

        times = []

        mode, alt, vel, quality = 0, 0, 0, 0
        heading, heading_std, roll, roll_std, pitch, pitch_std = 0, 0, 0, 0, 0, 0

        transformer = Transformer.from_crs("epsg:4612", "epsg:2451")
        lat_prev, lon_prev = None, None

        for t in ts:
            d = dict[t]
            # print(d)
            if "lat" in d:
                lat_prev = d["lat"]
            if "lon" in d:
                lon_prev = d["lon"]

            if lat_prev is None or lon_prev is None:
                continue

            lat = lat_prev
            lon = lon_prev

            alt = d["alt"] if "alt" in d else alt
            vel = d["vel"] if "vel" in d else vel
            mode = d["mode"] if "mode" in d else mode
            quality = d["quality"] if "quality" in d else quality

            heading = d["heading"] if "heading" in d else heading
            pitch = d["pitch"] if "pitch" in d else pitch
            roll = d["roll"] if "roll" in d else roll

            heading_std = d["heading_std"] if "heading_std" in d else heading_std
            pitch_std = d["pitch_std"] if "pitch_std" in d else pitch_std
            roll_std = d["roll_std"] if "roll_std" in d else roll_std

            if t1 == -1 or t1 <= t - times[0] <= t2:
                y, x = transformer.transform(lat, lon)
                xs.append(x)
                ys.append(y)
                zs.append(alt)

                lats.append(lat)
                lons.append(lon)

                vs.append(vel)
                modes.append(mode)
                qualities.append(quality)

                headings.append(heading)
                rolls.append(roll)
                pitchs.append(pitch)

                headings_std.append(heading_std)
                rolls_std.append(roll_std)
                pitchs_std.append(pitch_std)

                times.append(t - ts[0])

        return {
            "x": xs,
            "y": ys,
            "z": zs,
            "vel": vs,
            "lat": lats,
            "lon": lons,
            "mode": modes,
            "heading": headings,
            "roll": rolls,
            "pitch": pitchs,
            "heading_std": headings_std,
            "roll_std": rolls_std,
            "pitch_std": pitchs_std,
            "quality": qualities,
            "time": times,
        }


def plot_data(data):
    fig = plt.figure(figsize=(8, 12))

    # --- ① 速度 ---
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.plot(data["time"], data["vel"], label="velocity")
    ax1.set_xlabel("time(sec)")
    ax1.set_ylabel("velocity(m/s)")
    ax1.grid(True)
    ax1.legend()

    # --- ② 軌跡 ---
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.plot(data["x"], data["y"], label="trajectory", linewidth=1)

    # スタート・ゴール
    ax2.scatter(data["x"][0], data["y"][0], color="green", label="start", s=30)
    ax2.scatter(data["x"][-1], data["y"][-1], color="red", label="end", s=30)

    ax2.set_xlabel("X (m)")
    ax2.set_ylabel("Y (m)")
    # ax2.set_title("Trajectory")
    ax2.axis("equal")
    ax2.grid(True)
    ax2.legend()

    ax3 = fig.add_subplot(4, 1, 3)
    ax3.plot(data["time"], data["quality"], label="quality")
    ax3.plot(data["time"], data["mode"], label="mode")
    ax3.set_xlabel("time(sec)")
    ax3.set_ylabel("quality")
    ax3.grid(True)
    ax3.legend()

    # --- ④ Heading（あれば） ---
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.plot(data["time"], data["heading"], label="heading")
    ax4.plot(data["time"], data["roll"], label="roll")
    ax4.plot(data["time"], data["pitch"], label="pitch")

    ax4.set_xlabel("time(sec)")
    ax4.set_ylabel("std(deg)")
    ax4.grid(True)
    ax4.legend()
    ax4.set_xlabel("time(sec)")
    ax4.set_ylabel("heading(deg)")
    ax4.grid(True)
    ax4.legend()

    plt.tight_layout()
    plt.show()


def plot_heading_animation(data, step=5, arrow_scale=0.0001):

    lat = data["lat"]
    lon = data["lon"]
    heading = data["heading"]
    time = data["time"]

    # --- DataFrame化 ---
    df = pd.DataFrame({"lat": lat, "lon": lon, "heading": heading, "time": time})

    # --- heading → ベクトル変換 ---
    df["dx"] = df["heading"].apply(lambda h: math.cos(math.radians(h)))
    df["dy"] = df["heading"].apply(lambda h: math.sin(math.radians(h)))

    # --- フレーム生成 ---
    frames = []

    for i in range(0, len(df), step):
        frame_data = []

        # --- 点（現在位置） ---
        frame_data.append(
            go.Scattermapbox(
                lat=[df["lat"][i]],
                lon=[df["lon"][i]],
                mode="markers",
                marker=dict(size=10, color="blue"),
                name="position",
            )
        )

        # --- 矢印（heading方向） ---
        frame_data.append(
            go.Scattermapbox(
                lat=[df["lat"][i], df["lat"][i] + df["dy"][i] * arrow_scale],
                lon=[df["lon"][i], df["lon"][i] + df["dx"][i] * arrow_scale],
                mode="lines",
                line=dict(width=3, color="red"),
                name="heading",
            )
        )

        frames.append(go.Frame(data=frame_data, name=str(i)))

    # --- 初期表示 ---
    fig = go.Figure(data=frames[0].data, frames=frames)

    # --- レイアウト ---
    fig.update_layout(
        mapbox=dict(
            style="open-street-map", center=dict(lat=lat[0], lon=lon[0]), zoom=16
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 100, "redraw": True}}],
                    )
                ],
            )
        ],
    )

    fig.show()


def plot_heading_animation_with_slider(data, step=5, arrow_scale=0.0001):
    lat = data["lat"]
    lon = data["lon"]
    heading = data["heading"]
    time = data["time"]

    df = pd.DataFrame({"lat": lat, "lon": lon, "heading": heading, "time": time})

    # --- ベクトル化 ---
    df["dx"] = df["heading"].apply(lambda h: math.cos(math.radians(h)))
    df["dy"] = df["heading"].apply(lambda h: math.sin(math.radians(h)))

    frames = []
    slider_steps = []

    for i in range(0, len(df), step):
        frame = go.Frame(
            data=[
                # 点
                go.Scattermapbox(
                    lat=[df["lat"][i]],
                    lon=[df["lon"][i]],
                    mode="markers",
                    marker=dict(size=10, color="blue"),
                ),
                # 矢印
                go.Scattermapbox(
                    lat=[df["lat"][i], df["lat"][i] + df["dy"][i] * arrow_scale],
                    lon=[df["lon"][i], df["lon"][i] + df["dx"][i] * arrow_scale],
                    mode="lines",
                    line=dict(width=3, color="red"),
                ),
            ],
            name=str(i),
        )

        frames.append(frame)

        slider_steps.append(
            {
                "args": [[str(i)], {"frame": {"duration": 0, "redraw": True}}],
                "label": f"{int(df['time'][i])}s",
                "method": "animate",
            }
        )

    fig = go.Figure(data=frames[0].data, frames=frames)

    # --- スライダー ---
    sliders = [
        {
            "active": 0,
            "currentvalue": {"prefix": "Time: "},
            "pad": {"t": 50},
            "steps": slider_steps,
        }
    ]

    # --- レイアウト ---
    fig.update_layout(
        mapbox=dict(
            style="open-street-map", center=dict(lat=lat[0], lon=lon[0]), zoom=16
        ),
        sliders=sliders,
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 100, "redraw": True}}],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {"frame": {"duration": 0}, "mode": "immediate"},
                        ],
                    },
                ],
            }
        ],
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig.show()


def main():
    file = sys.argv[1]
    nmea = NMEA()
    nmea.load(file)

    data = nmea.get_data()
    plot_data(data)
    # plot_heading_animation(data)
    # plot_heading_animation_with_slider(data)


if __name__ == "__main__":
    main()
