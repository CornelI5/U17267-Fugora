import yaml
from fugora import FugoraEngine, CelestialObject, Vec3
from fugora.io import load_objects_from_config, save_state
from fugora.sources import NasaNeoSource


def on_anomaly(data):
    for a in data:
        print(f"[ALERT] Anomaly: {a.object_id} | Dev: {a.deviation:.4f}")


def on_data_ingested(data):
    if "NASA_NEO" in data:
        neo_data = data["NASA_NEO"]
        near_earth_objects = neo_data.get("near_earth_objects", {})
        count = sum(len(v) for v in near_earth_objects.values())
        print(f"[INFO] Ingested {count} NEOs from NASA")


def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    engine_cfg = config['engine']
    out_cfg = config['output']

    engine = FugoraEngine(dt=engine_cfg['dt'])
    engine.set_central_mass(engine_cfg['central_mass'])

    nasa_source = NasaNeoSource(api_key="DEMO_KEY")
    engine.sources.add_source(nasa_source)

    engine.events.subscribe("anomaly_detected", on_anomaly)
    engine.events.subscribe("data_ingested", on_data_ingested)

    objects_config = load_objects_from_config('config.yaml')
    for obj_conf in objects_config:
        obj = CelestialObject(
            obj_id=obj_conf['id'],
            name=obj_conf['name'],
            mass=obj_conf['mass'],
            position=Vec3(*obj_conf['position']),
            velocity=Vec3(*obj_conf['velocity']),
            radius=obj_conf.get('radius', 0),
            color=obj_conf.get('color', 'white'),
        )
        engine.add_object(obj)

    print(engine.summary())
    print("Starting simulation with live NASA data ingestion...")

    max_steps = engine_cfg['max_steps']
    engine.run(total_steps=max_steps)

    if out_cfg['save_state']:
        save_state(engine, filename=out_cfg['filename'])

    print("\n" + engine.summary())
    print("FUGORA v0.8 finished.")


if __name__ == "__main__":
    main()
