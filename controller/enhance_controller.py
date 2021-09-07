import os

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, request

from enhance_service import EnhanceService
from .error_handlers import build_response
from module.application_container import ApplicationContainer

folder_out = "static/output/"
os.makedirs(folder_out, exist_ok=True)

enhance_blueprint = Blueprint("enhance", __name__)


@enhance_blueprint.route("/enhance", methods=["POST"])
@inject
def detect(enhance_service: EnhanceService = Provide[ApplicationContainer.enhance_service]):
    urls = dict(request.get_json())['urls']
    output_result = enhance_service.process(urls, folder_out)
    return build_response(**output_result)
