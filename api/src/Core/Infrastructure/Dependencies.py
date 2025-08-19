"""
Dependencies for Core context
"""

from src.Core.DI.Container import Container
from src.Core.Logging.Logger import Logger
from src.Core.Tasks.TaskManager import TaskManager
from src.Core.Events.Bus import EventDispatcher
from src.Core.Infrastructure.Http.Controller import CoreController
from src.Config.AppConfig import AppConfig

class CoreDependencies:
    @staticmethod
    def register_dependencies(container: Container):
        container.register_singletons(
            {
                Logger.__name__: lambda container: Logger(
                    target=container.get(AppConfig.__name__).log_target
                ),
                EventDispatcher.__name__: lambda container: EventDispatcher(),
                TaskManager.__name__: lambda container: TaskManager(
                    logger=container.get(Logger.__name__)
                )
            }
        )

        container.register_factories(
            {
                CoreController.__name__: lambda container: CoreController(
                    task_manager=container.get(TaskManager.__name__),
                    logger=container.get(Logger.__name__),
                )
            }
        )
