from src.Config.AppConfig import AppConfig
from src.Core.DI.Container import Container
from src.Core.Logging.Logger import Logger
from dotenv import load_dotenv
from flask import Flask
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

# Setup Routes
# ...


# Index
@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the API!"}, 200


# Health Check
@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy"}, 200


# Catch-all route
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    return {"error": "Not Found"}, 404


# Run
if __name__ == "__main__":
    logger: Logger = container.get(Logger.__name__)
    app.run(host=appConfig.host, port=appConfig.port, debug=appConfig.debug)
