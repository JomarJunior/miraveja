# Standard Library
from typing import Any, Dict

import botocore.client
from boto3 import Session as Boto3Session
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from MiravejaCore.Shared.Configuration import AppConfig
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DI import container
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Domain.Services import EventRegistry, eventRegistry  # pylint: disable=W0611
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Keycloak.Infrastructure.KeycloakDependencies import KeycloakDependencies
from MiravejaCore.Shared.Logging.Factories import LoggerFactory
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Middlewares.Models import ErrorMiddleware, RequestResponseLoggingMiddleware
from sqlalchemy import Connection as DatabaseConnection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

from MiravejaApi.Events.Infrastructure.EventsDependencies import EventsDependencies
from MiravejaApi.Events.Infrastructure.Http.EventsController import EventsController
from MiravejaApi.Events.Infrastructure.Http.EventsRoutes import EventsRoutes
from MiravejaApi.Gallery.Infrastructure.GalleryDependencies import GalleryDependencies
from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController
from MiravejaApi.Gallery.Infrastructure.Http.GalleryRoutes import GalleryRoutes
from MiravejaApi.Member.Infrastructure.Http.MemberController import MemberController
from MiravejaApi.Member.Infrastructure.Http.MemberRoutes import MemberRoutes
from MiravejaApi.Member.Infrastructure.MemberDependencies import MemberDependencies

# Load environment variables from a .env file
load_dotenv()

# Load application configuration from environment variables
appConfig: AppConfig = AppConfig.FromEnv()

# Initialize the Container for Dependency Injection
container = Container.FromConfig(appConfig)

container.RegisterSingletons(
    {
        # Register Logger
        ILogger.__name__: lambda container: LoggerFactory.CreateLogger(
            **appConfig.loggerConfig.model_dump()  # pylint: disable=no-member
        ),
        # Database Engine
        DatabaseEngine.__name__: lambda container: create_engine(
            str(
                appConfig.databaseConfig.connectionUrl  # pylint: disable=no-member
            )  # enclosed in str() to satisfy linter
        ),
        # Boto3 S3 Client
        Boto3Session.client.__name__: lambda container: Boto3Session().client(
            "s3",
            endpoint_url=appConfig.minioConfig.endpointUrl,
            aws_access_key_id=appConfig.minioConfig.accessKey,
            aws_secret_access_key=appConfig.minioConfig.secretKey,
            region_name=appConfig.minioConfig.region,
            config=botocore.client.Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        ),
    }
)

eventRegistry.AttachLogger(container.Get(ILogger.__name__))

container.RegisterFactories(
    {
        # Database Connection
        DatabaseConnection.__name__: lambda container: container.Get(DatabaseEngine.__name__).connect(),
        # Database Session
        DatabaseSession.__name__: lambda container: sessionmaker(bind=container.Get(DatabaseEngine.__name__))(),
        # Unit of Work
        SqlDatabaseManagerFactory.__name__: lambda container: SqlDatabaseManagerFactory(
            resourceFactory=lambda: container.Get(DatabaseSession.__name__),
        ),
    }
)

# Register dependencies
KeycloakDependencies.RegisterDependencies(container)
MemberDependencies.RegisterDependencies(container)
GalleryDependencies.RegisterDependencies(container)
EventsDependencies.RegisterDependencies(container)

# Initialize FastAPI app
app: FastAPI = FastAPI(title=f"{appConfig.appName} API", version=appConfig.appVersion, redirect_slashes=False)

# Setup routers for API versioning
apiV1Router: APIRouter = APIRouter(prefix=f"/{appConfig.appName.lower()}/api/v1")  # pylint: disable=E1101

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Important: Handle preflight requests properly
    expose_headers=["Content-Type", "X-Content-Type-Options"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

app.add_middleware(RequestResponseLoggingMiddleware, logger=container.Get(ILogger.__name__))
app.add_middleware(ErrorMiddleware, logger=container.Get(ILogger.__name__))

# Keycloak Dependency Provider
keycloakDependencyProvider: KeycloakDependencyProvider = container.Get(KeycloakDependencyProvider.__name__)


# Index route
@apiV1Router.get("/", status_code=status.HTTP_200_OK)
async def Index() -> Dict[str, str]:
    return {"message": "Welcome to Miraveja API"}


# Health check route
@apiV1Router.get("/health", status_code=status.HTTP_200_OK)
async def Health() -> Dict[str, str]:
    return {"status": "healthy"}


# Protected route example using dependency injection for authentication
@apiV1Router.get("/protected")
async def Protected(user: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication)) -> Dict[str, Any]:
    return {
        "message": f"Hello, {user.username}! You have accessed a protected route.",
        "claims": user.model_dump(),
    }


# Modules routes
MemberRoutes.RegisterRoutes(apiV1Router, container.Get(MemberController.__name__), keycloakDependencyProvider)
GalleryRoutes.RegisterRoutes(apiV1Router, container.Get(GalleryController.__name__), keycloakDependencyProvider)
EventsRoutes.RegisterRoutes(apiV1Router, container.Get(EventsController.__name__), keycloakDependencyProvider)


# Catch-all route for undefined endpoints
@apiV1Router.get("/{full_path:path}", status_code=status.HTTP_404_NOT_FOUND)
async def CatchAll() -> Dict[str, str]:
    return {"error": "The requested resource was not found."}


# Include the API router in the main app
app.include_router(apiV1Router)
