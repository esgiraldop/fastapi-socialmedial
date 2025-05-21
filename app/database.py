"""Defines the database schema"""

import databases
import sqlalchemy
from config import config

metadata = sqlalchemy.MetaData()  # Stores info about database

### Defining the database schema ###
post_table = sqlalchemy.Table(
    "posts",
    metadata,  # Used by sqlAlchemy to store database metadata
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
)
comments_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column(
        "post_id", sqlalchemy.ForeignKey("posts.id", nullable=False)
    ),  # No need to specify integer, since metadata already figures that out from the primary key column
)


### Setting up database connection ###
engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # Only required for sqlite since it traditionally works single-threaded
)  # Engine allows sqlachemy to connect to a specific database

### Creating connection to the database ###
metadata.create_all(engine)  # To actually create the connection to the database
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)  # Object with which we will interact for the queries
