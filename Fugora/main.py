from fugora import FugoraEngine, CelestialObject, Vec3, OrbitVisualizer, AU, SUN_MASS, EARTH_MASS, JUPITER_MASS, MARS_MASS


def on_step(engine, step, anomalies):
    if anomalies:
        for a in anomalies:
            print(f"[ANOMALY] {a.object_id} | deviation: {a.deviation:.4f} | t={a.timestamp:.0f}s")


def main():
    engine = FugoraEngine(dt=3600)

    sun = CelestialObject(
        obj_id="SUN", name="Sun", mass=SUN_MASS,
        position=Vec3(0, 0, 0), velocity=Vec3(0, 0, 0),
        radius=6.96e8, color="yellow",
    )

    earth = CelestialObject(
        obj_id="EARTH", name="Earth", mass=EARTH_MASS,
        position=Vec3(AU, 0, 0), velocity=Vec3(0, 29780, 0),
        radius=6.371e6, color="dodgerblue",
    )

    mars = CelestialObject(
        obj_id="MARS", name="Mars", mass=MARS_MASS,
        position=Vec3(1.524 * AU, 0, 0), velocity=Vec3(0, 24070, 0),
        radius=3.39e6, color="tomato",
    )

    jupiter = CelestialObject(
        obj_id="JUPITER", name="Jupiter", mass=JUPITER_MASS,
        position=Vec3(5.203 * AU, 0, 0), velocity=Vec3(0, 13070, 0),
        radius=6.99e7, color="orange",
    )

    asteroid = CelestialObject(
        obj_id="U17267", name="Fugora Target", mass=1.0e12,
        position=Vec3(2.5 * AU, 0.3 * AU, 0),
        velocity=Vec3(-3000, 18000, 500),
        radius=5000, color="cyan",
    )

    engine.add_object(sun)
    engine.add_object(earth)
    engine.add_object(mars)
    engine.add_object(jupiter)
    engine.add_object(asteroid)

    print(engine.summary())
    print("\nStarting visualization...")

    viz = OrbitVisualizer(engine, interval_ms=30)
    viz.show(total_frames=5000)

    print("\n" + engine.summary())


if __name__ == "__main__":
    main()
