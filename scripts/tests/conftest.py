import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def synthetic_run(tmp_path):
    """Synthetic run/walk: 2 x (240 s run @ 180 W, HR 140 / 60 s walk @ 110 W, HR 130).
    No real athlete data is ever used in tests."""
    time, hr, watts, cad, moving = [], [], [], [], []
    t = 0
    for _ in range(2):
        for _ in range(240):
            time.append(t); hr.append(140 if t % 240 < 200 else 150); watts.append(180)
            cad.append(78); moving.append(True); t += 1
        for _ in range(60):
            time.append(t); hr.append(130); watts.append(110); cad.append(57)
            moving.append(True); t += 1
    streams = {"time": time, "heart_rate": hr, "watts": watts, "cadence": cad, "moving": moving}
    sp = tmp_path / "streams.json"
    sp.write_text(json.dumps(streams))
    laps = {"lapGroups": [{"type": 10, "laps": [
        {"lapIndex": 1, "time": 240.0, "avgPower": 180, "avgHr": 142, "maxHr": 150,
         "avgCadence": 156, "groundTime": 300, "strideHeight": 80, "avgStrideLength": 90,
         "legStiffness": 110},
        {"lapIndex": 2, "time": 60.0, "avgPower": 110, "avgHr": 130, "maxHr": 131,
         "avgCadence": 114, "groundTime": 600, "strideHeight": 75, "avgStrideLength": 70,
         "legStiffness": 105},
        {"lapIndex": 3, "time": 240.0, "avgPower": 180, "avgHr": 142, "maxHr": 150,
         "avgCadence": 156, "groundTime": 300, "strideHeight": 80, "avgStrideLength": 90,
         "legStiffness": 110},
        {"lapIndex": 4, "time": 60.0, "avgPower": 110, "avgHr": 130, "maxHr": 131,
         "avgCadence": 114, "groundTime": 600, "strideHeight": 75, "avgStrideLength": 70,
         "legStiffness": 105},
    ]}]}
    lp = tmp_path / "laps.json"
    lp.write_text(json.dumps(laps))
    zp = tmp_path / "zones.yaml"
    zp.write_text("version: 2000-01-01\nhr_max_bpm: 190\nrun:\n  z1_cap_bpm: 145\n"
                  "  lthr_bpm: 170\nbike:\n  z1_cap_bpm: 135\n  lthr_bpm: null\nprovisional: []\n")
    dp = tmp_path / "detail.txt"
    dp.write_text("Average Power: 166 W\nPerceived Effort: Very Easy\nWorkout Note: all good\n")
    return {"streams": str(sp), "laps": str(lp), "zones": str(zp), "detail": str(dp), "raw": streams}
