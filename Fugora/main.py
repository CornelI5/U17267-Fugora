import yaml
from fugora import FugoraEngine, CelestialObject, Vec3
from fugora.io import load_objects_from_config, save_state
from fugora.sources import NasaNeoSource


def on_anomaly(data):
    for a in data:
        print(f"[ALERT] Anomaly: {a.object_id} | Dev: {a.deviation:.4f}")


def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    engine_cfg = config['engine']
    perm_cfg = config['permissions']
    out_cfg = config['output']

    allow_ext = perm_cfg['allow_external_updates']
    
    if allow_ext:
        print("External data updates are ENABLED by config.")
    else:
        print("External data updates are DISABLED. Set 'allow_external_updates: true' in config.yaml to enable.")

    engine = FugoraEngine(dt=engine_cfg['dt'], cpu_cores=4, allow_external=allow_ext)
    engine.set_central_mass(engine_cfg['central_mass'])

    if allow_ext:
        nasa_source = NasaNeoSource(api_key="DEMO_KEY")
        engine.sources.add_source(nasa_source)

    engine.events.subscribe("anomaly_detected", on_anomaly)

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
    print("Starting simulation...")

    max_steps = engine_cfg['max_steps']
    engine.run(total_steps=max_steps)

    if out_cfg['save_state']:
        save_state(engine, filename=out_cfg['filename'])

    print("\n" + engine.summary())
    print("FUGORA v1.0 finished.")


if __name__ == "__main__":
    main()d.")


if __name__ == "__main__":
    main()
