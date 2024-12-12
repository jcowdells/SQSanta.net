import sqlite3
from enum import Enum
from log.log import *

class DataType(Enum):
    TEXT        = "TEXT"
    INTEGER     = "INTEGER"
    REAL        = "REAL"
    PRIMARY_KEY = "INTEGER PRIMARY KEY AUTOINCREMENT"
    FOREIGN_KEY = "INTEGER"

def run_sql(*args):
    connection = sqlite3.connect("app.db")
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    cursor.execute(*args)
    connection.commit()
    info("Running SQL Statement:")
    for arg in args:
        info(arg)
    return cursor.fetchall()

def create_table(table_name, **columns):
    columns_string = ""
    count = 0
    for name, datatype in columns.items():
        debug(datatype)
        unknown_type = False
        if isinstance(datatype, tuple):
            if len(datatype) != 2:
                unknown_type = True
            if datatype[0] != DataType.FOREIGN_KEY:
                unknown_type = True
            else:
                datatype = DataType.FOREIGN_KEY
        if not isinstance(datatype, DataType):
            unknown_type = True
        if unknown_type:
            raise ValueError(f"Could not understand datatype: {datatype}")
        else:
            if count != 0:
                columns_string += ",\n"
            columns_string += f"{name} {datatype.value}"
            count += 1

    for name, datatype in columns.items():
        if isinstance(datatype, tuple) and datatype[0] == DataType.FOREIGN_KEY:
            columns_string += f",\nFOREIGN KEY ({name}) REFERENCES {datatype[1]}({name})"

    sqlstring = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    {columns_string}
    )
    """
    run_sql(sqlstring)

def insert_table(table_name, **columns):
    unknown_string = ", ".join(["?" for _ in range(len(columns))])
    sqlstring = f"""
    INSERT INTO {table_name}({', '.join(columns.keys())}) VALUES ({unknown_string})
    """
    values = tuple(columns.values())
    run_sql(sqlstring, values)
