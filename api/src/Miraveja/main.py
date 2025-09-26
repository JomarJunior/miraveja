# Standard Library
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware

# Configuration
from Miraveja.Configuration.Models import AppConfig

# Shared
from Miraveja.Shared.DI.Models import Container
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Logging.Factories import LoggerFactory
from Miraveja.Shared.Middlewares.Models import ErrorMiddleware, RequestResponseLoggingMiddleware

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


# Index route
@apiV1Router.get("/", status_code=status.HTTP_200_OK)
async def Index() -> Dict[str, str]:
    return {"message": "Welcome to Miraveja API"}


# Health check route
@apiV1Router.get("/health", status_code=status.HTTP_200_OK)
async def Health() -> Dict[str, str]:
    return {"status": "healthy"}


# Include the API router in the main app
app.include_router(apiV1Router)
