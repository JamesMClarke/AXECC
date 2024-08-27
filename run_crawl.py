import os, json, re, csv, argparse, sys, subprocess
from tqdm import tqdm
from time import sleep
from common import *
import difflib

def create_containers():
    """
    Function to run the logic for creating containers
    """
    print("Creating docker containers")

    if platform == "darwin":
        command1 = f"docker-compose -f docker/docker-compose.yaml -p {sql_name} up --build -d "
    elif platform == "linux" or platform == 'linux2':
        command1 = prefix + f"docker compose -f docker/docker-compose.yaml -p {sql_name} up --build -d"
    else:
        print("System not supported")
        exit()


    os.system(command1)

def run_crawl(relative_path, visit_time):
    """
    Function to run the crawl
    """
    print("Running crawl")


    if platform == 'darwin':
        command1 = prefix + f"docker exec -it {sql_name}-mitmproxy-1 mitmdump -q -s /src/docker/log_traffic.py /src/extensions"+relative_path
        command2 = prefix + f"docker exec -it {sql_name}-automation-1 node crawl.mjs /src/extensions"+relative_path +" "+ str(visit_time*1000)

        process1 = subprocess.Popen(command1.split(), shell=False)  # Split command into arguments
        process2 = subprocess.Popen(command2.split(), shell=False)
    else:
        command1 = prefix + f"docker exec -i {sql_name}-mitmproxy-1 mitmdump -q -s /src/docker/log_traffic.py /src/extensions"+relative_path
        command2 = prefix + f"docker exec -i {sql_name}-automation-1 node crawl.mjs /src/extensions"+relative_path +" "+ str(visit_time*1000)

        process1 = subprocess.Popen(command1, shell=True)  # Split command into arguments
        process2 = subprocess.Popen(command2, shell=True)

    # Wait for crawl to finish
    process2.wait()

def cleanup():
    """
    Function to stop and remove all docker containers
    """
    print("Stopping and removing docker containers")

    command1 = prefix + f"docker stop {sql_name}-web_server-1"
    command2 = prefix + f"docker stop {sql_name}-mitmproxy-1"
    command3 = prefix + f"docker stop {sql_name}-automation-1"

    if platform == 'darwin':
        process1 = subprocess.Popen(command1.split(), shell=False)
        process2 = subprocess.Popen(command2.split(), shell=False)
        process3 = subprocess.Popen(command3.split(), shell=False)
    else:
        process1 = subprocess.Popen(command1, shell=True)
        process2 = subprocess.Popen(command2, shell=True)
        process3 = subprocess.Popen(command3, shell=True)

    process1.wait()
    process2.wait()
    process3.wait()

    command1 = prefix + f"docker rm {sql_name}-web_server-1"
    command2 = prefix + f"docker rm {sql_name}-mitmproxy-1"
    command3 = prefix + f"docker rm {sql_name}-automation-1"

    if platform == 'darwin':
        process1 = subprocess.Popen(command1.split(), shell=False)
        process2 = subprocess.Popen(command2.split(), shell=False)
        process3 = subprocess.Popen(command3.split(), shell=False)
    else:
        process1 = subprocess.Popen(command1, shell=True)
        process2 = subprocess.Popen(command2, shell=True)
        process3 = subprocess.Popen(command3, shell=True)

    process1.wait()
    process2.wait()
    process3.wait()


parser = argparse.ArgumentParser("Run a crawl based on an sql file")
parser.add_argument("sql", help="Input the name of the sql file to be processed.", type=str)
parser.add_argument("vist_time", help="Input the length of time to vist the honeypage for in Secconds", type=int)
parser.add_argument('pwd', help="Input your sudo password", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
sql_file = args.sql
vist_time = args.vist_time
pwd = args.pwd
verbose = args.verbose

sql_name = os.path.basename(sql_file).split(".")[0]

#Check if csv file exists
if(os.path.isfile(sql_file)):
    print("File %s exists, starting crawl \n" %(sql_name))
    print("The program will visit the page for %s seconds \n" %(str(vist_time)))
else:
    print("File %s doesn't exists, stopping" %(sql_file))
    sys.exit()

cwd = os.getcwd()
#relative_path = sql_file.replace(cwd,"")
relative_path = sql_file.split('extensions')[-1]
platform = sys.platform
prefix = ""
if platform == "linux" or platform == "linux2":
    prefix = f'echo {pwd} | sudo -S '

create_containers()
sleep(2)
run_crawl(relative_path, vist_time)
sleep(2)
cleanup()
