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

def select_all(conn, table):
    ''' Selects all from a sqlite file and returns all rows'''
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    return c.fetchall()

def select_where(conn, table, element, value):
    '''Selects all from sqlite table where element equals value'''
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE {element} = {value}")
    return c.fetchall()

def select_column(conn, column):
    c = conn.cursor()
    c.execute(f"SELECT {column} FROM extensions")
    return [row[0] for row in c.fetchall()]

def drop_table(conn, table):
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table}")
