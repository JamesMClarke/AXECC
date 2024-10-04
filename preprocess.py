from pathlib import Path
import os, argparse, sys, csv, zipfile, _thread, subprocess
from tqdm import tqdm
from time import sleep
from common import *
import unicodedata


def unzip_folder(zip_file_path, extract_to_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

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
        file = unicodedata.normalize('NFD', file)
        #Checks if there is a file to unzip
        #if(os.path.isfile(os.path.join(crx_dir, file))):
            #Check if folder already exists
        if(os.path.isdir(os.path.join(unzip_dir, file.split('.')[0]))):
            if verbose:
                tqdm.write("Folder already exists")
                tqdm.write(file)
                #tqdm.write(row[1])

        #Try to unzip file
        try:
            #with zipfile.ZipFile(os.path.join(crx_dir,file), 'r') as zip_ref:
            #zip_ref.extractall(os.path.join(unzip_dir,file.split('.')[0]))
            #extract_zip_safely(os.path.join(crx_dir,file),os.path.join(unzip_dir,file.split('.')[0]))
            crx_file = os.path.join(crx_dir,file)
            output_folder = os.path.join(unzip_dir,file.split('.')[0])
            #command = f'7z x "{crx_file}" -o"{output_folder}"'
            #result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            unzip_folder(crx_file, output_folder)
            unzipped += 1
        except Exception as e :
            if verbose:
                tqdm.write("Error unzipping %s"%file)
                tqdm.write(str(e))
            errors += 1
            errors_file = open('Error Unzip.csv', 'a', encoding='utf-8')
            errors_file.write(file+','+str(e)+','+'\n')
            errors_file.close()
        #else:
        #    tqdm.write("File %s doesn't exist"%file)

        pbar.update(1)

#Check if all files could be unzipped
if errors != 0:
    print("%s files couldn't be unzipped, see Error Unzip.csv for details"%(errors))

files_in_dir = len([d for d in os.listdir(unzip_dir) if os.path.isdir(os.path.join(unzip_dir, d))])

#Check that the number of files in the dir match the number in the csv file
if no_rows == files_in_dir:
    print("Finished unzipping successfully")
else:
    print("Some files have not been unzipped")
    print("There are %s in the csv file" % no_rows)
    print("%s files have been unzipped" % unzipped)    