import datetime
from enum import Enum

class Level(Enum):
    DEBUG   = "DEBUG"
    INFO    = "INFO"
    WARNING = "WARNING"
    ERROR   = "ERROR"

def log(message, level):
    if isinstance(level, Level):
        level = level.value
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {level}: {message}")

def debug(message):
    log(message, Level.DEBUG)

def info(message):
    log(message, Level.INFO)

def warning(message):
    log(message, Level.WARNING)

def error(message):
    log(message, Level.ERROR)
