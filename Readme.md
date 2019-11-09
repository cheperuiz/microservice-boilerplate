## RESTful API

Your resources' & corresponding endpoints will be defined as part of this microservice, but requests will be handled by the `apigateway` microservice. To accomplish that, the following steps are needed:

## Resources (Endpoints)

-   Make sure the container is mounting your resource file at the `APIGATEWAY_RESOURCES_DIR/<your-resource>.py` location (ie. `${APIGATEWAY_RESOURCES_DIR}/generic.py`).
-   Import your resources to `APIGATEWAY_ROOT/app/api/api_factory.py` and register your resources inside the `create_api` function.

## Celery Tasks

-   Define the name of the Celery queues where your workers will be listening to dispatch task requests (This is usually an `ENV` variable or a field in your config file).
-   Finally, register your Celery tasks in `APIGATEWAY_RESOURCES_DIR/tasks.py`. Note that your tasks can be named anything, as long as a celery worker can math the `name` property with a real celery task. Refer to the [Celery docs](http://docs.celeryproject.org/en/latest/index.html) for more detailed information.

## Model

Migrations scripts allow you to:

-   Create the database(if it doesen't exist yet).
-   Create the needed tables for your model.
-   Update all the tables that might need change after the model is change.

Note that migrations are not tracked by this repository, you might want to change that behavior.

### First time

-   To initialize the migrations, create the db, etc, you need to run the commands below:

`docker-compose run generic bash -c "cd /generic/src/database && python manage.py db init"`
`docker-compose run generic bash -c "cd /generic/src/database && python manage.py db migrate"`

-   If you are using sqlalchemy-utils as part of your model, in the version created by the `migrate` command, you need to import the library:
    `import sqlalchemy_utils`

### After every change to the model (or during startup)

docker-compose run generic bash -c "cd /generic/src/database && python manage.py db upgrade"
