import yaml
from fugora import FugoraEngine, CelestialObject, Vec3, OrbitVisualizer
from fugora.io import load_objects_from_config, save_state
from fugora.sources import DummySatelliteSource


def on_anomaly(data):
    for a in data:
        print(f"[ALERT] Anomaly detected: {a.object_id} | Dev: {a.deviation:.4f}")


def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    engine_cfg = config['engine']
    viz_cfg = config['visualization']
    out_cfg = config['output']

    engine = FugoraEngine(dt=engine_cfg['dt'])
    engine.set_central_mass(engine_cfg['central_mass'])

    sat_source = DummySatelliteSource()
    engine.sources.add_source(sat_source)

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

    max_steps = engine_cfg['max_steps']
    
    if viz_cfg['enabled']:
        from fugora.visualization import OrbitVisualizer
        viz = OrbitVisualizer(engine, interval_ms=viz_cfg['interval_ms'])
        viz.show(total_frames=max_steps)
    else:
        engine.run(total_steps=max_steps)

    if out_cfg['save_state']:
        save_state(engine, filename=out_cfg['filename'])

    print("\n" + engine.summary())
    print("FUGORA v0.7 finished.")


if __name__ == "__main__":
    main()
