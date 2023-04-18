import os
from models import *
db = PostgresqlDatabase(
    os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST"),
    port=os.environ.get("POSTGRES_PORT"))


def main():
    db.connect()
    db.create_tables([TestModel])
    TestModel.create(name="Test")
    # Here we run the server.
    while True:
        pass

    
if __name__ == "__main__":
    main()