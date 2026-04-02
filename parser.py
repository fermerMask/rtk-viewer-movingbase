def parse_hrp(lines):
    result = []

    for line in lines:
        if "$PSSN,HRP" in line:
            parts = line.split(",")
            try:
                heading = float(parts[3])
                roll = float(parts[6])

                result.append({"heading": heading, "roll": roll})
            except:
                continue
    return result
