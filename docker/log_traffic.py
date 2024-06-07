"""
Logs to file while using mitmproxy
Run 'mitmproxy -s log_to_file.py'
"""
import asyncio, logging, datetime, time, os, sys, threading, sqlite3
from mitmproxy.script import concurrent

sqlite_file = sys.argv[-1]

def get_ext(conn ):
    """
    Function to get the current extension being ran from the sqlite file
    :return: Returns the current extension
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM current_ext")
    return cur.fetchall()[0][1]

def add_request(request, conn):
    """
    Function to add a single request to a sqlite file
    """
    ext = get_ext(conn)
    sql = """INSERT INTO requests (url, extension, port, method, http_version, headers, content, trailers, timestamp_start, timestamp_end) VALUES (?,?,?,?,?,?,?,?,?,?);"""
    cur = conn.cursor()
    cur.execute(sql,(request.host+request.path, ext, request.port, request.method, request.http_version, str(request.headers), request.content, str(request.trailers), request.timestamp_start, request.timestamp_end))
    conn.commit()

def create_table(conn):
    """
    Create requests table
    """
    sql = """ CREATE TABLE IF NOT EXISTS requests (
requestID INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    extension TEXT,
    port INTEGER,
    method TEXT,
    http_version TEXT,
    headers TEXT,
    content TEXT,
    trailers TEXT,
    timestamp_start TEXT,
    timestamp_end TEXT
    );"""
    c = conn.cursor()
    c.execute(sql)

conn = sqlite3.connect(sqlite_file)
create_table(conn)

# Hooks can be async, which allows the hook to call async functions and perform async I/O
# without blocking other requests. This is generally preferred for new addons.
async def request(flow):
    #logger.info(f"Request: {flow.request.host}{flow.request.path}")
    #print(f"Request: {flow.request.host}{flow.request.path}")
    add_request(flow.request, conn)
    #logger.info(f"start  request: {flow.request.host}{flow.request.path}")
