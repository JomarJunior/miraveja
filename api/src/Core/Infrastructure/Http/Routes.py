"""
Core HTTP Routes
"""

from src.Core.Infrastructure.Http.Controller import CoreController
from flask import Blueprint, request, Response

class CoreRoutes:
    @staticmethod
    def register_routes(blueprint: Blueprint, controller: CoreController):
        @blueprint.route("/tasks/<string:task_id>", methods=["GET"])
        def get_task_status(task_id: str) -> Response:
            return controller.get_task_status(request, task_id)
