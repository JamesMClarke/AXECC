from pathlib import Path
import sqlite3
from sqlite3 import Error

def create_directory(directory_path):
    """ Function to try create dir if it doesn't exist """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def sort_dic(dic):
    """ Function to sort a dictionary """
    return dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    
    return conn

def create_table(conn, sql):
    """Create a table based on connection and sql"""
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def insert_data(conn, sql, data):
    """ Insert into a databases given connection, sql and data"""
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()