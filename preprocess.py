from pathlib import Path
import os, argparse, sys, csv, zipfile, _thread, subprocess
from tqdm import tqdm
from time import sleep
from common import *

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename):
    # Replace invalid characters with an underscore or other valid character
    invalid_chars = '<>:"/\\|?*'
    sanitized_filename = ''.join('_' if c in invalid_chars else c for c in filename)
    return sanitized_filename

def extract_zip_safely(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            # Sanitize the filename
            original_filename = member.filename
            sanitized_filename = sanitize_filename(original_filename)

            # Prepare the target path
            target_path = os.path.join(extract_to, sanitized_filename)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Extract the file
            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

current_dir = os.getcwd()

#TODO: Add the ablity to include multiple folders
#Take input of csv file
parser = argparse.ArgumentParser("Preprocess extensions")
parser.add_argument("sql", help="Input the name of the sqlite file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
sql_file = args.sql
verbose = args.verbose

sql_name = os.path.basename(sql_file).split(".")[0]

#Check if csv file exists
#sql_file = os.path.join(current_dir,sql_file)
#print(sql_file)
category_folder = os.path.dirname(sql_file)
#print(all_files)
#quit()
if(os.path.isfile(sql_file)):
    print("File %s exists, starting preprocessing" %(sql_name))
else:
    print("File %s doesn't exists, stopping" %(sql_file))
    sys.exit()

#all_files = os.path.join(current_dir,"extensions")
#category_folder = os.path.join(all_files, sql_name)

#Set dir for crx files
crx_dir = os.path.join(category_folder,"crx_files")
#Create folder for files to be unzipped into
unzip_dir = os.path.join(category_folder,"preprocessed")
create_directory(unzip_dir)
print("Unzipping all crx files into folder: %s" %(unzip_dir))

#Unzip all crxs in csv file
errors = 0
unzipped = 0

conn = create_connection(sql_file)
files = select_column(conn, 'file')

no_rows = len(files)
with tqdm(total=no_rows) as pbar:
    for file in files:
        #Checks if there is a file to unzip
        if(os.path.isfile(os.path.join(crx_dir, file))):
            #Check if folder already exists
            if(os.path.isdir(os.path.join(unzip_dir, file.split('.')[0]))):
                if verbose:
                    tqdm.write("Folder already exists")
                    tqdm.write(file)
                    #tqdm.write(row[1])

            #Try to unzip file
            try:
                #with zipfile.ZipFile(os.path.join(crx_dir,file), 'r') as zip_ref:
                #    unzipped += 1
                #zip_ref.extractall(os.path.join(unzip_dir,file.split('.')[0]))
                extract_zip_safely(os.path.join(crx_dir,file),os.path.join(unzip_dir,file.split('.')[0]))
            except Exception as e :
                if verbose:
                    tqdm.write("Error unzipping %s"%file)
                    tqdm.write(str(e))
                errors += 1
                errors_file = open('Error Unzip.csv', 'a', encoding='utf-8')
                errors_file.write(file+','+str(e)+','+'\n')
                errors_file.close()
        else:
            tqdm.write("File %s doesn't exist"%file)

        pbar.update(1)

#Check if all files could be unzipped
if errors != 0:
    print("%s files couldn't be unzipped, see Error Unzip.csv for details"%(errors))

print(unzipped)

files_in_dir = len([d for d in os.listdir(unzip_dir) if os.path.isdir(os.path.join(unzip_dir, d))])

#Check that the number of files in the dir match the number in the csv file
if no_rows == files_in_dir:
    print("Finished unzipping successfully")
else:
    print("Some files have not been unzipped")
    print("There are %s in the csv file" % no_rows)
    print("%s files have been unzipped" % files_in_dir)    


print("Trying to Deobfuscate and de-minify")


with tqdm(total=no_rows) as pbar:
    for file in files:
        if file != "error":
            file_name = file.split('.')[0]

            #Set location of uzipped folder
            unzipped_ext = os.path.join(unzip_dir,file_name)

            #For all files,including sub dirs, in the unzipped folder
            for dirpath, dirnames, filenames in os.walk(unzipped_ext):
                for filename in filenames:
                    #If the file is javascript or html
                    if filename.endswith(".js") or filename.endswith(".html"):
                        #Set filepath
                        filepath = os.path.join(dirpath, filename)
                        if(verbose):
                            pbar.write("Deobfuscating and de-minifying %s" %filepath)

                        for attempt in range(5):
                                try:
                                    #Run js-beautify
                                    command = 'js-beautify "'+filepath+'" -r'
                                    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                                    if verbose:
                                        pbar.write(result.stdout)
                                    break
                                except Exception as e:
                                    if attempt == 4:  # This is the last attempt
                                        tqdm.write(filepath+" couldn't be saved")
                                        errors_file = open('Error Processing.txt', 'a', encoding='utf-8')
                                        errors_file.write(filepath + " "+ str(e)+'\n')
                                        errors_file.close()
                                        #raise  # Re-raise the last exception

        pbar.update(1)
