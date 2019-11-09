# pylint: disable=import-error
from datetime import datetime
from flask import request, g
from flask_restplus import Resource
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from werkzeug.exceptions import UnprocessableEntity

# pylint: disable=no-name-in-module
from utils.common import make_jsend_response, uuid_factory
from app.resources.tasks import (
    get_all_generic_models,
    get_generic_models_by_uuids,
    create_generic_model,
    delete_generic_models,
    update_generic_model,
)

ma = Marshmallow()


class GenericModelSchema(ma.Schema):
    uuid = fields.String(dump_only=True)
    name = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # Correlation IDs:
    user_id = fields.Integer(required=True, load_only=True)


summary = ["uuid", "name"]
details = ["uuid", "name", "created_at", "updated_at"]
updatable_values = ["name"]

generic_model_schema = GenericModelSchema()  # internal use only
generic_model_summary_schema = GenericModelSchema(only=summary)
generic_models_summary_schema = GenericModelSchema(many=True, only=summary)
generic_model_details_schema = GenericModelSchema(only=details)
generic_models_details_schema = GenericModelSchema(many=True, only=details)
generic_model_update_schema = GenericModelSchema(only=updatable_values)


class GenericModelsList(Resource):
    def get(self):
        generic_models = get_all_generic_models.delay().get()
        return make_jsend_response(data=generic_models)

    def post(self):
        json_data = request.get_json(force=True)
        json_data["user_id"] = 0  # TODO: Set auth & correct g.user.id
        try:
            generic_model_data = generic_model_schema.load(json_data)
            r = create_generic_model.delay(generic_model_data)
            uuid = r.get()
        except ValidationError as err:
            raise UnprocessableEntity(err.args) from None

        return make_jsend_response(data=uuid, code=201)


class GenericModelsDetails(Resource):
    def get(self, uuids):
        uuids = uuids.split(",")
        generic_models = get_generic_models_by_uuids.delay(uuids).get()
        if not generic_models:
            return make_jsend_response(code=404)
        return make_jsend_response(data=generic_models)

    def delete(self, uuids):
        uuids = uuids.split(",")
        deleted_uuids = delete_generic_models.delay(uuids).get()
        if not deleted_uuids:
            return make_jsend_response(404)
        return make_jsend_response(202, data=deleted_uuids)

    def put(self, uuids):
        json_data = request.get_json(force=True)  # force option ignores mimetype
        json_data["uuid"] = uuids
        try:
            uuid = update_generic_model.delay(json_data).get()
        except ValidationError as err:
            raise UnprocessableEntity(err.args) from None
        if not uuid:
            return make_jsend_response(code=404)
        return make_jsend_response(data=uuid)
