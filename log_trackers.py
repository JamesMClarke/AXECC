"""
Logs to file while using mitmproxy
Run 'mitmdump -s log_to_file.py'

Need to run webserver python3 -m http.server -b 127.0.0.1 -d .
"""
import logging, sqlite3
from sqlite3 import Error
from mitmproxy.script import concurrent  
from common import *

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    
    return conn

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS trackers (
                                        id integer PRIMARY KEY,
                                        extension text,
                                        tracker_url text
                                    ); """)
    except Error as e:
        print(e)

def create_tracker(conn, tracker):
    sql = ''' INSERT INTO trackers(extension,tracker_url) VALUES (?,?)'''
    cur = conn.cursor()
    cur.execute(sql, tracker)
    conn.commit()

#Variables 
web_page = 'http://localhost:8081/'
extension_name = "None"
db_file = ("temp.sqlite")

conn = create_connection(db_file)
create_table(conn)
conn.close()

#Handle a connecting and log to file
async def request(flow):
    with open("current_ext.txt", "r") as f:
        ext = f.read()
        f.close()

    conn = create_connection(db_file)
    create_tracker(conn, (ext, flow.request.host+flow.request.path))
    conn.close()
    #logger.info(f"start  request: {flow.request.host}{flow.request.path}")


