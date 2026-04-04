def dm_to_deg(dm, direction):
    if dm == "" or dm is None:
        return None

    dm = float(dm)
    d = int(dm / 100)
    m = dm - d * 100
    deg = d + m / 60

    if direction in ["S", "W"]:
        deg *= -1

    return deg


def parse_nmea(lines):
    records = {}

    for line in lines:
        parts = line.split(",")

        # =========================
        # RMC（位置・速度）
        # =========================
        if "$GPRMC" in line or "$GNRMC" in line:
            try:
                t = parts[1]
                status = parts[2]

                if status != "A":
                    continue

                lat = dm_to_deg(parts[3], parts[4])
                lon = dm_to_deg(parts[5], parts[6])

                speed = float(parts[7]) * 0.514444 if parts[7] != "" else 0.0

                if t not in records:
                    records[t] = {}

                records[t]["lat"] = lat
                records[t]["lon"] = lon
                records[t]["speed"] = speed

            except:
                continue

        # =========================
        # HRP（pitch / roll / heading）
        # =========================
        if "$PSSN,HRP" in line:
            try:
                t = parts[2]

                heading = float(parts[4]) if parts[4] != "" else 0.0
                pitch = float(parts[6]) if parts[6] != "" else 0.0
                roll = float(parts[7]) if parts[7] != "" else 0.0

                if t not in records:
                    records[t] = {}

                records[t]["heading"] = heading
                records[t]["pitch"] = pitch
                records[t]["roll"] = roll

            except:
                continue

    # =========================
    # ソート
    # =========================
    times = sorted(records.keys())

    lat_list = []
    lon_list = []
    speed_list = []
    pitch_list = []
    roll_list = []
    heading_list = []

    last_pitch = 0
    last_roll = 0
    last_heading = 0

    for t in times:
        data = records[t]

        # RMCがない場合スキップ
        if "lat" not in data or "lon" not in data:
            continue

        lat_list.append(data["lat"])
        lon_list.append(data["lon"])
        speed_list.append(data.get("speed", 0.0))

        # HRPは欠損補完
        pitch = data.get("pitch", last_pitch)
        roll = data.get("roll", last_roll)
        heading = data.get("heading", last_heading)

        pitch_list.append(pitch)
        roll_list.append(roll)
        heading_list.append(heading)

        last_pitch = pitch
        last_roll = roll
        last_heading = heading

    return lat_list, lon_list, speed_list, pitch_list, roll_list, heading_list