# pylint: disable=import-error
import sys
import os
import socket
from marshmallow import ValidationError
from sqlalchemy import exc
from werkzeug.exceptions import UnprocessableEntity
from datetime import datetime

# pylint: disable=no-name-in-module
from models.generic import GenericModel, GenericModelSchema
from events.events import GenericEvent, EventType
from events.redisstream import RedisStream, produce_one, start_redis_consumer
from utils.celery import CeleryManager
from utils.configmanager import ConfigManager
from utils.common import uuid_factory

celery = CeleryManager.get_instance(
    use_flask=True
)  # Flask is needed because the model is defined using flask-sqlalchemy
queues = os.environ["QUEUES"]


summary = ["uuid", "name"]
details = ["uuid", "name", "created_at", "updated_at"]
updatable_values = ["name"]


generic_model_schema = GenericModelSchema()  # internal use only
generic_models_schema = GenericModelSchema(many=True)  # internal use only
generic_model_summary_schema = GenericModelSchema(only=summary)
generic_models_summary_schema = GenericModelSchema(many=True, only=summary)
generic_model_details_schema = GenericModelSchema(only=details)
generic_models_details_schema = GenericModelSchema(many=True, only=details)
generic_model_update_schema = GenericModelSchema(only=updatable_values)


class GenericModelTask(celery.Task):
    def __init__(self):
        self.registered_handlers = {EventType.FRAMEPRODUCER_STARTED: explore}


@celery.task(bind=True, base=GenericModelTask, task_track_started=True, queue=queues)
def get_all_generic_models(self, schema=generic_models_summary_schema):
    generic_models = GenericModel.get_all()
    return schema.dump(generic_models)


@celery.task(bind=True, base=GenericModelTask, task_track_started=True, queue=queues)
def get_generic_models_by_uuids(self, uuids, schema=generic_models_details_schema):
    generic_models = GenericModel.get_many(uuid=uuids)
    return schema.dump(generic_models)


@celery.task(bind=True, base=GenericModelTask, task_track_started=True)
def create_generic_model(self, generic_model_data):
    try:
        generic_model = generic_model_schema.load(generic_model_data)
        generic_model.save()
    except (exc.IntegrityError, exc.SQLAlchemyError) as err:
        message = err.args
        if type(message) is tuple and "DETAIL" in message[0]:
            message = message[0].split("DETAIL:  ")[1]
        raise ValidationError(message) from None
    produce_one(
        "generic_models",
        GenericEvent(
            generic_model_data=generic_model_schema.dump(generic_model),
            event_type=EventType.GENERIC_MODEL_CREATED,
        ),
    )
    return generic_model.uuid


@celery.task(bind=True, base=GenericModelTask, task_track_started=True, queue=queues)
def delete_generic_models(self, uuids):
    generic_models = GenericModel.get_many(uuid=uuids)
    ids = [generic_model.id for generic_model in generic_models]  # Could be a subset of received uuids
    uuids = [generic_model.uuid for generic_model in generic_models]  # Could be a subset of received uuids
    generic_models_data = generic_models_schema.dump(generic_models)
    GenericModel.delete(ids)
    for generic_model_data in generic_models_data:
        produce_one(
            "generic_models",
            GenericEvent(generic_model_data=generic_model_data, event_type=EventType.GENERIC_MODEL_DELETED),
        )
    return uuids


@celery.task(bind=True, base=GenericModelTask, task_track_started=True, queue=queues)
def update_generic_model(self, new_data):
    generic_model = GenericModel.get_first(uuid=new_data["uuid"])
    if generic_model:
        try:
            _valid = generic_model_schema.load(new_data, partial=True, transient=True)
            _valid_fields = generic_model_update_schema.dump(_valid)
            new_data = {k: v for k, v in _valid_fields.items() if v is not None}
            generic_model_data = generic_model_update_schema.dump(generic_model)
            generic_model_data["updated_at"] = datetime.now()
            generic_model_data.update(new_data)  # Update generic_model properties
            generic_model.update(generic_model_data)
            produce_one(
                "generic_models",
                GenericEvent(
                    generic_model_data=generic_model_schema.dump(generic_model),
                    event_type=EventType.GENERIC_MODEL_UPDATED,
                ),
            )
            return generic_model.uuid
        except (exc.IntegrityError, exc.SQLAlchemyError) as err:
            message = err.args
            if type(message) is tuple and "DETAIL" in message[0]:
                message = message[0].split("DETAIL:  ")[1]
            raise ValidationError(message) from None
    return None


def explore(redis_generic_model_name, event, event_id):
    pass


@celery.task(bind=True, base=GenericModelTask, task_track_started=True, queue=queues)
def consume_events_forever(self, consumer_group_config):
    start_redis_consumer(consumer_group_config, self.registered_handlers)

