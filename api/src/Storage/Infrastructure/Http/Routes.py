"""
Routes definitions for Storage context
"""

from src.Storage.Infrastructure.Http.Controller import StorageController
from flask import Blueprint, request, Response

class StorageRoutes:
    @staticmethod
    def register_routes(
        blueprint: Blueprint,
        controller: StorageController
    ):
        @blueprint.route("/images", methods=["GET"])
        def list_all_images() -> Response:
            return controller.list_all_images(request)

        @blueprint.route("/images", methods=["POST"])
        def register_image() -> Response:
            return controller.register_image(request)

        @blueprint.route("/images/<int:image_id>", methods=["GET"])
        def find_image_by_id(image_id) -> Response:
            return controller.find_image_by_id(request, image_id)

        @blueprint.route("/providers", methods=["GET"])
        def list_all_providers() -> Response:
            return controller.list_all_providers(request)

        @blueprint.route("/providers", methods=["POST"])
        def register_provider() -> Response:
            return controller.register_provider(request)

        @blueprint.route("/providers/<int:provider_id>", methods=["GET"])
        def find_provider_by_id(provider_id) -> Response:
            return controller.find_provider_by_id(request, provider_id)

        @blueprint.route("/images/<int:image_id>/contents", methods=["GET"])
        def download_image_content(image_id) -> Response:
            return controller.download_image_content(request, image_id)

        @blueprint.route("/images/contents", methods=["POST"])
        def upload_image_content() -> Response:
            return controller.upload_image_content(request)