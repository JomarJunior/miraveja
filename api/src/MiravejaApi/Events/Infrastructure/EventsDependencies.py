from MiravejaCore.Shared.DI.Models import Container

from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Services import (
    EventFactory,
    EventDeserializerService,
    EventValidatorService,
    EventRegistry,
    eventRegistry,
)
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Events.Infrastructure.Json.Registry import JsonSchemaRegistry
from MiravejaCore.Shared.Events.Infrastructure.EventsDependencies import EventsDependencies as CoreEventsDependencies
from MiravejaApi.Events.Application.ConnectStream import ConnectStreamHandler
from MiravejaApi.Connection.Domain.Models import WebSocketConnectionManager
from MiravejaApi.Events.Infrastructure.Http.EventsController import EventsController


class EventsDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        CoreEventsDependencies.RegisterDependencies(container)
        container.RegisterFactories(
            {
                # Registries
                EventRegistry.__name__: lambda container: eventRegistry,
                JsonSchemaRegistry.__name__: lambda container: JsonSchemaRegistry(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig"))
                ),
                # Services
                EventDeserializerService.__name__: lambda container: EventDeserializerService(
                    _eventRegistry=container.Get(EventRegistry.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                EventValidatorService.__name__: lambda container: EventValidatorService(
                    schemaRegistry=container.Get(JsonSchemaRegistry.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                WebSocketConnectionManager.__name__: lambda container: WebSocketConnectionManager(
                    logger=container.Get(ILogger.__name__),
                ),
                EventFactory.__name__: lambda container: EventFactory(
                    deserializerService=container.Get(EventDeserializerService.__name__),
                    validatorService=container.Get(EventValidatorService.__name__),
                ),
                # Handlers
                ConnectStreamHandler.__name__: lambda container: ConnectStreamHandler(
                    websocketConnectionManager=container.Get(WebSocketConnectionManager.__name__),
                    eventFactory=container.Get(EventFactory.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                # Controller
                EventsController.__name__: lambda container: EventsController(
                    connectStreamHandler=container.Get(ConnectStreamHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
