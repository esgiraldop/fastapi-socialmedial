"""Defines the database schema"""

import databases
import sqlalchemy
from app.config import config
from sqlalchemy import Column, Integer, String, ForeignKey, Table

metadata = sqlalchemy.MetaData()  # Stores info about database

### Defining the database schema ###
post_table = Table(
    "posts",
    metadata,  # Used by sqlAlchemy to store database metadata
    Column("id", Integer, primary_key=True),
    Column("body", String),
    Column(
        "user_id", ForeignKey("users.id"), nullable=False
    ),  # Links the posts table with the users table
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
)

comments_table = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("body", String),
    Column(
        "post_id", Integer, ForeignKey("posts.id"), nullable=False
    ),  # Specifying integer for consistency purposes, but here is actually no need to specify it, since metadata already figures that out from the primary key column
    Column(
        "user_id", ForeignKey("users.id"), nullable=False
    ),  # Links the posts table with the users table
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
