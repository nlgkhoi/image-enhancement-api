import json
import logging
import traceback

from domain.errors import RError, InternalError


def handle_defined_errors(error: RError):
    return build_error_response(error)


def handle_other_exceptions(error: Exception):
    return build_error_response(InternalError(str(error), error))


def build_response(**kwargs):
    response = {}
    response.update(kwargs)
    return json.dumps(response)


def build_error_response(error: RError):
    print(error)
    if error.__cause__ is not None:
        logging.error("".join(traceback.TracebackException.from_exception(error.__cause__).format()))
    else:
        logging.error(error.message)
    return {
        "error": error.get_error(),
        "message": error.message
    }
