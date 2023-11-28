from api.database.schemas.row_schema import RowSchema
import logging
from api import Api


class RowRepository:
    def insert_one(self, data):
        row_schema = RowSchema()
        logging.info("testing 1")
        row_col = Api.collection("rows")
        row_model = row_schema.load(data)
        row_col.insert_one(row_model)
        logging.info("testing 2")
        print("row_model: ", row_model)
