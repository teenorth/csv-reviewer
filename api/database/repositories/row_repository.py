from api.database.schemas.row_schema import RowSchema
import logging


class RowRepository:
    def insert_one(self, data):
        row_schema = RowSchema()
        logging.info("testing 1")
        row_model = row_schema.load(data)
        logging.info("testing 2")
        print("row_model: ", row_model)
