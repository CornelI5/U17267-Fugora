import json
import os


def save_state(engine, filename="state.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    state = engine.get_state()
    
    with open(filename, 'w') as f:
        json.dump(state, f, indent=4)
    
    print(f"State saved to {filename}")


def load_objects_from_config(config_path):
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    objects_config = config.get('simulation', {}).get('objects', [])
    return objects_config
