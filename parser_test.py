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


def parse_rmc(lines):
    lat_list = []
    lon_list = []
    speed_list = []
    for line in lines:
        if "$GPRMC" in line or "$GNRMC" in line:
            parts = line.split(",")

            try:
                lat = dm_to_deg(parts[3], parts[4])
                lon = dm_to_deg(parts[5], parts[6])
                speed = float(parts[7]) * 0.51444

                if lat is not None and lon is not None:
                    lat_list.append(lat)
                    lon_list.append(lon)
                    speed_list.append(speed)

            except:
                continue

    return lat_list, lon_list, speed_list
