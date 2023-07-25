"""
Logs to file while using mitmproxy
Run 'mitmproxy -s log_to_file.py'
"""
import asyncio, logging, datetime, time, os, sys, threading
from mitmproxy.script import concurrent  
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/Users/jc02788/Documents/accessiblity_extensions/logfile.log')
logger.addHandler(handler)

logger.info("Starting %s" %(datetime.datetime.now()))


# Hooks can be async, which allows the hook to call async functions and perform async I/O
# without blocking other requests. This is generally preferred for new addons.
async def request(flow):
    logger.info(f"Request: {flow.request.host}{flow.request.path}")
    #logger.info(f"start  request: {flow.request.host}{flow.request.path}")