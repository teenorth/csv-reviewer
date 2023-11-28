from marshmallow import Schema, fields as m_fields, post_load
from bson.objectid import ObjectId
from typing import Dict


class RowModel:
    def __init__(
        self,
        _id: ObjectId,
        base_id: ObjectId,
        table_id: ObjectId,
        timeline_id: ObjectId,
        fields: Dict[str, str],
    ):
        self._id = _id
        self.base_id = base_id
        self.table_id = table_id
        self.timeline_id = timeline_id
        self.fields = fields


class RowSchema(Schema):
    _id = m_fields.String()
    base_id = m_fields.String()
    table_id = m_fields.String(required=True)
    timeline_id = m_fields.String(required=True)
    fields = m_fields.Dict(keys=m_fields.String(), values=m_fields.String())

    @post_load
    def make_model(self, data, **kwargs):
        return RowModel(**data)
