from src.Config.AppConfig import AppConfig
from src.Core.DI.Container import Container
from dotenv import load_dotenv
import sqlalchemy as sa

# Load environment variables
load_dotenv()

# Initialize the app config
appConfig = AppConfig.from_env()

# Initialize the container
container = Container()

# Singletons registrations
container.register_singletons({
    AppConfig.__name__: lambda container: appConfig,
    sa.engine.Engine.__name__: lambda container: sa.create_engine(appConfig.database_url),
})

# Factories registrations
container.register_factories({
    sa.Connection.__name__: lambda container: container.get(sa.engine.Engine.__name__).connect()
})
