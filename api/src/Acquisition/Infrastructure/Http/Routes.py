"""
Routes definitions for Acquisition context
"""

from src.Acquisition.Infrastructure.Http.Controller import AcquisitionController
from flask import Blueprint, request, Response

class AcquisitionRoutes:
    @staticmethod
    def register_routes(
        blueprint: Blueprint,
        controller: AcquisitionController
    ):
        @blueprint.route("/acquisition/acquire-images", methods=["POST"])
        def acquire_images() -> Response:
            return controller.acquire_images(request)