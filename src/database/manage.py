# pylint: disable=import-error
# pylint: disable=no-name-in-module
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from app.app_factory import make_flask
from database.postgres import db_config, db
from utils.common import make_url

# Import all your models here:
from models.generic import GenericModel

app = make_flask()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

engine = create_engine(make_url(db_config))
if not database_exists(engine.url):
    create_database(engine.url)

if __name__ == "__main__":
    manager.run()

