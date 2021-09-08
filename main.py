import logging
import os
import sys

from dependency_injector import containers
from dependency_injector.wiring import Provide, inject
from flask import Flask
from py_profiler.profiler_controller import profiler_blueprint
from waitress import serve

from controller import enhance_controller, enhance_blueprint
from controller.error_handlers import handle_defined_errors, handle_other_exceptions
from domain.errors import RError
from module import ApplicationContainer
from module.injector import create_injector
from utils.setup_logging import setup_logging


@inject
def setup_http_server(
        injector: containers.DeclarativeContainer,
        port: int = Provide[ApplicationContainer.config.server.http.port.as_int()],
        nthreads: int = Provide[ApplicationContainer.config.server.http.nthreads.as_int()],
) -> None:
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.debug = True

    app.register_blueprint(enhance_blueprint)
    app.register_blueprint(profiler_blueprint)

    app.register_error_handler(RError, handle_defined_errors)
    app.register_error_handler(Exception, handle_other_exceptions)

    logging.info(f"Created http server at port = {port} with {nthreads} concurrent threads.")
    serve(
        app, host="0.0.0.0",
        port=port,
        threads=nthreads if nthreads is not None else 4
    )

if __name__ == "__main__":
    os.environ['APP_MODE'] = sys.argv[1] if len(sys.argv) > 1 else 'development'
    setup_logging()
    injector = create_injector([
        sys.modules[__name__],
        enhance_controller,
    ], mode=os.environ['APP_MODE'])
    setup_http_server(injector)
