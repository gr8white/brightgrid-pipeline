import json, uuid, random
from datetime import datetime, timedelta
from pathlib import Path

VOLUME_PATH    = "/Volumes/brightgrid/bronze/raw_readings"
ZONES          = [f"ZONE_{i:02d}" for i in range(1, 9)]
FACILITY_TYPES = ["residential", "commercial", "industrial"]
STATUSES       = ["normal", "normal", "normal", "normal", "normal", "anomaly", "offline", "fault"]
FIRMWARE       = ["v2.1.4", "v2.1.5", "v2.2.0", "v2.2.1"]

def generate_batch(n_meters=100, batch_id=1, fault_rate=0.05):
    readings = []
    now = datetime.utcnow()

    for _ in range(n_meters):
        meter_id      = f"MTR_{random.randint(10000, 99999)}"
        facility_type = random.choice(FACILITY_TYPES)
        base_kwh      = {"residential": 0.8, "commercial": 4.5, "industrial": 22.0}[facility_type]
        status        = "fault" if random.random() < fault_rate else random.choice(STATUSES)

        # Faults show abnormal voltage and consumption spikes
        if status == "fault":
            voltage    = round(random.uniform(180, 195), 2)   # under-voltage
            reading_kwh = round(base_kwh * random.uniform(3.0, 6.0), 3)  # consumption spike
        elif status == "anomaly":
            voltage    = round(random.uniform(235, 250), 2)   # over-voltage
            reading_kwh = round(base_kwh * random.uniform(1.8, 2.5), 3)
        elif status == "offline":
            voltage    = 0.0
            reading_kwh = 0.0
        else:
            voltage    = round(random.uniform(215, 225), 2)
            reading_kwh = round(base_kwh * random.uniform(0.7, 1.3), 3)

        readings.append({
            "reading_id":       str(uuid.uuid4()),
            "meter_id":         meter_id,
            "customer_id":      f"CUST_{random.randint(100000, 999999)}",
            "facility_type":    facility_type,
            "grid_zone_id":     random.choice(ZONES),
            "reading_kwh":      reading_kwh,
            "voltage":          voltage,
            "status":           status,
            "reading_ts":       (now - timedelta(minutes=random.randint(0, 45))).isoformat(),
            "firmware_version": random.choice(FIRMWARE),
        })

    path = Path(VOLUME_PATH)
    output_file = path / f"readings_batch_{batch_id:04d}.json"
    with open(output_file, "w") as f:
        for r in readings:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(readings)} readings to {output_file}")