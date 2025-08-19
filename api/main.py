# Config
from src.Config.AppConfig import AppConfig
# Core
from src.Core.DI.Container import Container
from src.Core.Logging.Logger import Logger
from src.Core.Infrastructure.Dependencies import CoreDependencies
from src.Core.Infrastructure.Http.Routes import CoreRoutes
from src.Core.Infrastructure.Http.Controller import CoreController
# Storage
from src.Storage.Infrastructure.Dependencies import StorageDependencies
from src.Storage.Infrastructure.Http.Routes import StorageRoutes
from src.Storage.Infrastructure.Http.Controller import StorageController
# Acquisition
from src.Acquisition.Infrastructure.Dependencies import AcquisitionDependencies
from src.Acquisition.Infrastructure.Http.Routes import AcquisitionRoutes
from src.Acquisition.Infrastructure.Http.Controller import AcquisitionController
# Extras
from dotenv import load_dotenv
import argparse
from flask import Flask, Blueprint, Request, request
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy import Connection as DatabaseConnection
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa

# Load environment variables
load_dotenv()

# Initialize the app config
appConfig = AppConfig.from_env()

# Initialize the container
container = Container.from_app_config(appConfig)

# Singletons registrations
container.register_singletons(
    {
        AppConfig.__name__: lambda container: appConfig,
        DatabaseEngine.__name__: lambda container: sa.create_engine(
            appConfig.database_url
        ),
    }
)

# Factories registrations
container.register_factories(
    {
        DatabaseConnection.__name__: lambda container: container.get(
            DatabaseEngine.__name__
        ).connect(),
        DatabaseSession.__name__: lambda container: sessionmaker(
            bind=container.get(DatabaseEngine.__name__)
        )(),
    }
)

# Context dependencies
CoreDependencies.register_dependencies(container)
StorageDependencies.register_dependencies(container)
AcquisitionDependencies.register_dependencies(container)

app = Flask(appConfig.app_name)

# Setup blueprints for API versions
v1_api = Blueprint("v1", __name__, url_prefix=f"/{appConfig.app_name.lower()}/api/v1")

# Setup Routes
CoreRoutes.register_routes(v1_api, container.get(CoreController.__name__))
StorageRoutes.register_routes(v1_api, container.get(StorageController.__name__))
AcquisitionRoutes.register_routes(v1_api, container.get(AcquisitionController.__name__))

# ...

# Index
@v1_api.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the API!"}, 200

# Health Check
@v1_api.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy"}, 200

# Testing
@v1_api.route("/testing", methods=["POST"])
def testing():
    return {"status": "testing"}, 200

@v1_api.route("/testing", methods=["GET"])
def testing_get():
    return {"status": "testing"}, 200

@v1_api.route("/test_database", methods=["GET"])
def test_database():
    db_connection: DatabaseConnection = container.get(DatabaseConnection.__name__)
    result = db_connection.execute(sa.text("SELECT 1")).scalar_one()
    return {"result": result}, 200

# Catch-all route
@v1_api.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    return {"error": "Not Found"}, 404

# Register blueprints
app.register_blueprint(v1_api)

# Register middlewares
@app.before_request
def before_request():
    logger: Logger = container.get(Logger.__name__)
    logger.info("=" * 50)
    logger.info("MiraVeja API")
    logger.info("Incoming request...")
    logger.info(f"[{request.method}] {request.path}")
    request_data = request.get_json(silent=True)
    # remove method and path
    logger.info(f"Data: {request_data}")
    extra_data = {}
    for key, value in request.headers:
        extra_data[key] = value
    extra_data["remote_addr"] = request.remote_addr

    logger.info(f"\n{extra_data}")
    logger.info("+" * 50)

@app.after_request
def after_request(response):
    logger: Logger = container.get(Logger.__name__)
    logger.info("End of processing request")
    logger.info("=" * 50)
    return response

# Register CLI parameters
parser = argparse.ArgumentParser(
    prog=appConfig.app_name,
    description="API for MiraVeja image gallery",
    epilog="pre-alpha"
)

parser.add_argument(
    '--mode',
    choices=['server', 'testing'],
    default='server',
    help="Run mode"
)

# Run
if __name__ == "__main__":
    args = parser.parse_args()
    if args.mode == 'server':
        logger: Logger = container.get(Logger.__name__)
        app.run(host=appConfig.host, port=appConfig.port, debug=appConfig.debug)
    else:
        logger: Logger = container.get(Logger.__name__)
        logger.info("Running in testing mode")