import os

from .application_container import ApplicationContainer


def create_injector(
        modules: list,
        mode: str = 'development'
):
    os.environ['APP_MODE'] = mode if mode is not None else os.environ['APP_MODE']
    mode = os.environ['APP_MODE']

    print(f"Mode: {mode}")
    print(f"Loaded config: config/{mode}.yml")
    print(f"Modules: {modules}")
    injector = ApplicationContainer()
    injector.config.from_yaml(f"conf/{mode}.yml")
    injector.wire(modules)
    print("Wire completed")

    return injector
