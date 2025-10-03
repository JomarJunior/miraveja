# Standard Library
from typing import Any, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, status, Depends
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from Miraveja.Configuration.Models import AppConfig

# Shared
from Miraveja.Shared.DI.Models import Container
from Miraveja.Shared.Keycloak.Infrastructure.KeycloakDependencies import KeycloakDependencies
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Logging.Factories import LoggerFactory
from Miraveja.Shared.Middlewares.Models import ErrorMiddleware, RequestResponseLoggingMiddleware
from Miraveja.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser

# Load environment variables from a .env file
load_dotenv()

# Load application configuration from environment variables
appConfig: AppConfig = AppConfig.FromEnv()

# Initialize the Container for Dependency Injection
container = Container.FromAppConfig(appConfig)

container.RegisterSingletons(
    {
        ILogger.__name__: lambda container: LoggerFactory.CreateLogger(
            **appConfig.loggerConfig.model_dump()  # pylint: disable=no-member
        )
    }
)

# Register dependencies
KeycloakDependencies.RegisterDependencies(container)

# Initialize FastAPI app
app: FastAPI = FastAPI(title=f"{appConfig.appName} API", version=appConfig.appVersion)

# Setup routers for API versioning
apiV1Router: APIRouter = APIRouter(prefix=f"/{appConfig.appName.lower()}/api/v1")  # pylint: disable=E1101

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Include the API router in the main app
app.include_router(apiV1Router)
