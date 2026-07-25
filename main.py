import yaml
from fugora import FugoraEngine, CelestialObject, Vec3
from fugora.io import load_objects_from_config
from fugora.sources import NasaNeoSource
from fugora.gl_viz import start_gl_viz


def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    engine_cfg = config['engine']
    perm_cfg = config['permissions']
    viz_cfg = config.get('visualization', {})

    allow_ext = perm_cfg['allow_external_updates']

    engine = FugoraEngine(dt=engine_cfg['dt'], cpu_cores=4, allow_external=allow_ext)
    engine.set_central_mass(engine_cfg['central_mass'])

    if allow_ext:
        nasa_source = NasaNeoSource(api_key="DEMO_KEY")
        engine.sources.add_source(nasa_source)
        nasa_source.parse_to_objects(engine)
        
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

    w = viz_cfg.get('width', 1280)
    h = viz_cfg.get('height', 800)

    print("Starting FUGORA OpenGL 3D...")
    start_gl_viz(engine, width=w, height=h)


if __name__ == "__main__":
    main()
