import sqlite3
from datetime import datetime

DB_NAME = "books.db"
def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


