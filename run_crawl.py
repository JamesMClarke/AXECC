import os, argparse, sys, subprocess
from time import sleep
from common import *

def create_containers(page_type):
    """
    Function to run the logic for creating containers
    """
    print("Creating docker containers")
    docker_compose = ""
    if page_type == "login_page":
        docker_compose = "login_page.yaml"
        print("Creating containers with the inaccessible login page as the honeypage")
    else:
        docker_compose = "wordpress.yaml"
        print("Creating containers with the WordPress as the honeypage")

    if platform == "darwin":
        command1 = f"docker-compose -f docker/{docker_compose} -p {sql_name} up --build -d "
    elif platform == "linux" or platform == 'linux2':
        command1 = prefix + f"docker compose -f docker/{docker_compose} -p {sql_name} up --build -d"
    else:
        print("System not supported")
        exit()


    os.system(command1)

def run_subprocess_command(command, platform):
    """Helper function to run subprocess commands based on platform
    Args:
        command (str): Command to execute
        platform (str): Operating system platform
    Returns:
        subprocess.Popen: Process handle
    """
    return subprocess.Popen(
        command.split() if platform == 'darwin' else command,
        shell=platform != 'darwin'
    )

def run_crawl(relative_path, visit_time, page_type, visit_url):
    """
    Function to run the crawl
    """
    print("Running crawl")


    if platform == 'darwin':
        command1 = prefix + f"docker exec -it {sql_name}-mitmproxy-1 mitmdump -q -s /src/docker/log_traffic.py /src/extensions{relative_path}"
        command2 = prefix + f"docker exec -it {sql_name}-automation-1 node crawl.mjs /src/extensions{relative_path} {str(visit_time*1000)} --{page_type} '{visit_url}'"

        process1 = subprocess.Popen(command1.split(), shell=False)  # Split command into arguments
        process2 = subprocess.Popen(command2.split(), shell=False)
    else:
        command1 = prefix + f"docker exec -i {sql_name}-mitmproxy-1 mitmdump -q -s /src/docker/log_traffic.py /src/extensions"+relative_path
        command2 = prefix + f"docker exec -i {sql_name}-automation-1 node crawl.mjs /src/extensions{relative_path} {str(visit_time*1000)} --{page_type} '{visit_url}'"

        process1 = subprocess.Popen(command1, shell=True)  # Split command into arguments
        process2 = subprocess.Popen(command2, shell=True)

    # Wait for crawl to finish
    process2.wait()

def cleanup(page_type):
    """
    Function to stop and remove all docker containers
    """
    print("Stopping and removing docker containers")

    # Stop containers
    stop_commands = [
        f"docker stop {sql_name}-web_server-1",
        f"docker stop {sql_name}-mitmproxy-1", 
        f"docker stop {sql_name}-automation-1"
    ]

    if page_type == "wordpress":
        stop_commands.append(f"docker stop {sql_name}-db-1")

    processes = [run_subprocess_command(prefix + cmd, platform) for cmd in stop_commands]
    for p in processes:
        p.wait()

    # Remove containers
    remove_commands = [
        f"docker rm {sql_name}-web_server-1",
        f"docker rm {sql_name}-mitmproxy-1",
        f"docker rm {sql_name}-automation-1"
    ]

    if page_type == "wordpress":
        remove_commands.append(f"docker rm {sql_name}-db-1")

    processes = [run_subprocess_command(prefix + cmd, platform) for cmd in remove_commands]
    for p in processes:
        p.wait()

platform = sys.platform 

parser = argparse.ArgumentParser("Run a crawl based on an sql file")
parser.add_argument("sql", help="Input the name of the sql file to be processed.", type=str)
parser.add_argument("vist_time", help="Input the length of time to vist the honeypage for in Secconds", type=int)
if platform == "linux" or platform == "linux2":
    parser.add_argument('pwd', help="Input your sudo password", type=str)
parser.add_argument("-v",'--verbose', action='store_true')

# Add mutually exclusive group for login_page and wordpress
page_type_group = parser.add_mutually_exclusive_group()
page_type_group.add_argument("--login_page", action="store_const", const="login_page", dest="page_type", default="login_page", help="Specify to use the inaccessible login page as the honeypage")
page_type_group.add_argument("--wordpress", type=str, dest="page_type", help="Specify the url of the wordpress page you want to visit.")

args = parser.parse_args()
sql_file = args.sql
visit_time = args.vist_time
if platform == "linux" or platform == "linux2":
    pwd = args.pwd
else:
    pwd = ""
verbose = args.verbose
page_type = args.page_type

visit_url = ""
if page_type != "login_page":
    visit_url = page_type
    page_type = "wordpress"

sql_name = os.path.basename(sql_file).split(".")[0]

#Check if sqlite file exists
if(os.path.isfile(sql_file)):
    print("File %s exists, starting crawl \n" %(sql_name))
    print("The program will visit the page for %s seconds \n" %(str(visit_time)))
else:
    print("File %s doesn't exists, stopping" %(sql_file))
    sys.exit()

cwd = os.getcwd()
#relative_path = sql_file.replace(cwd,"")
relative_path = sql_file.split('extensions')[-1]

prefix = ""
if platform == "linux" or platform == "linux2":
    prefix = f'echo {pwd} | sudo -S '

create_containers(page_type)
sleep(2)
run_crawl(relative_path, visit_time, page_type, visit_url)
sleep(2)
cleanup(page_type)