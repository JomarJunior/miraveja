from src.Config.AppConfig import AppConfig
from src.Core.DI.Container import Container
from src.Core.Logging.Logger import Logger
from dotenv import load_dotenv
from flask import Flask, Blueprint
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy import Connection as DatabaseConnection
import sqlalchemy as sa

# Load environment variables
load_dotenv()

# Initialize the app config
appConfig = AppConfig.from_env()

# Initialize the container
container = Container()

# Singletons registrations
container.register_singletons(
    {
        AppConfig.__name__: lambda container: appConfig,
        DatabaseEngine.__name__: lambda container: sa.create_engine(
            appConfig.database_url
        ),
        Logger.__name__: lambda container: Logger(appConfig.log_target),
    }
)

# Factories registrations
container.register_factories(
    {
        DatabaseConnection.__name__: lambda container: container.get(
            DatabaseEngine.__name__
        ).connect()
    }
)

app = Flask(appConfig.app_name)

# Setup blueprints for API versions
v1_api = Blueprint("v1", __name__, url_prefix=f"/{appConfig.app_name.lower()}/api/v1")

# Setup Routes
# ...

@v1_api.route("/test_database", methods=["GET"])
def test_database():
    db_connection: DatabaseConnection = container.get(DatabaseConnection.__name__)
    result = db_connection.execute(sa.text("SELECT 1")).scalar_one()
    return {"result": result}, 200

# Index
@v1_api.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the API!"}, 200


# Health Check
@v1_api.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy"}, 200


# Catch-all route
@v1_api.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    return {"error": "Not Found"}, 404

# Register blueprints
app.register_blueprint(v1_api)

# Run
if __name__ == "__main__":
    logger: Logger = container.get(Logger.__name__)
    app.run(host=appConfig.host, port=appConfig.port, debug=appConfig.debug)
