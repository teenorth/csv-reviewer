from marshmallow import Schema
from marshmallow.fields import *


class RowUpdate(Schema):
    _id = String(required=True)
    fields = Dict(keys=String(), values=Raw())


class CreateReview(Schema):
    message = String(required=True)
    updates = List(Nested(RowUpdate))
