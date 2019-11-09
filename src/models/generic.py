# pylint: disable=import-error
# pylint: disable=no-name-in-module
import datetime
import time
from sqlalchemy import ForeignKey, Column, String, Float, Boolean, BigInteger, DateTime
from sqlalchemy.orm import validates
from sqlalchemy_utils import URLType
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from models.interface.base import IBase, ma
from utils.common import uuid_factory


class GenericModel(IBase):
    __tablename__ = "generic_models"
    id = Column(BigInteger(), primary_key=True)

    uuid = Column(String(), unique=True, default=lambda: uuid_factory("GENERIC"))
    name = Column(String(), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.now())
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.now())

    # Correlation ID
    user_id = Column(BigInteger())


class GenericModelSchema(ma.ModelSchema):
    class Meta:
        model = GenericModel

    uuid = fields.String(missing=uuid_factory("GENERIC"))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    # Correlation IDs:
    user_id = fields.Integer(required=True, load_only=True)

