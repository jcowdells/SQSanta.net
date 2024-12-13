import sqlite3
from enum import Enum
from log.log import *

class DataType(Enum):
    TEXT        = "TEXT"
    INTEGER     = "INTEGER"
    REAL        = "REAL"
    PRIMARY_KEY = "INTEGER PRIMARY KEY AUTOINCREMENT"
    FOREIGN_KEY = "INTEGER"

DATABASE = "app.db"

def run_sql(*args):
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    cursor.execute(*args)
    connection.commit()
    info("Running SQL Statement:")
    for arg in args:
        if isinstance(arg, str):
            arg = arg.strip()
        info(arg)
    return cursor.fetchall()

def run_sql_get_id(*args):
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    cursor.execute(*args)
    connection.commit()
    info("Running SQL Statement:")
    for arg in args:
        if isinstance(arg, str):
            arg = arg.strip()
        info(arg)
    return cursor.lastrowid

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
    return run_sql_get_id(sqlstring, values)

def update_table(table_name, primary_key, primary_value, **columns):
    unknown_string = ", ".join([f"{name} = ?" for name in columns.keys()])
    sqlstring = f"""
    UPDATE {table_name}
    SET {unknown_string}
    WHERE {primary_key} = ?
    """
    values = (*list(columns.values()), primary_value)
    run_sql(sqlstring, values)

def delete_from_table(table_name, condition="AND", **columns):
    unknown_string = f" {condition} ".join([f"{name} = ?" for name in columns.keys()])
    sqlstring = f"""
    DELETE FROM {table_name}
    WHERE {unknown_string}
    """
    values = tuple(columns.values())
    run_sql(sqlstring, values)
