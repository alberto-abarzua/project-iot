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
    db.create_tables([Data, Logs, Config, Loss])
    # while True:
    #     pass

    # add config
    Config.create(config_name="config2", id_protocol=1, transport_layer="TCP")


    
if __name__ == "__main__":
    main()