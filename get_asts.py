from pathlib import Path
import os, argparse, sys, csv, subprocess
from tqdm import tqdm
from time import sleep
from common import *

current_dir = os.getcwd()

#Take input of csv file
parser = argparse.ArgumentParser("Generate ASTs")
parser.add_argument("csv", help="Input the name of the csv file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
csv_file = args.csv
verbose = args.verbose

csv_name = os.path.basename(csv_file).split(".")[0]

#Check if csv file exists
csv_file = os.path.join(current_dir,csv_file)
if(os.path.isfile(csv_file)):
    print("File %s exists, starting to generate ASTs" %(csv_name))
else:
    print("File %s doesn't exists, stopping" %(csv_file))
    sys.exit()

unzip_dir = os.path.join(current_dir,"preprocessed",csv_name)

#Set dir for crx files
ast_dir = os.path.join(current_dir,"ASTs",csv_name)
create_directory(ast_dir)
print("Putting ASTs in folder: %s" %(ast_dir))

print("Trying to generate ASTs")

with open(csv_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    no_rows = len(rows)
    with tqdm(total=no_rows) as pbar:
        for row in rows:
            #Get filename and remove .crx
            file = row[7]
            if file != "error":
                file_name = file.split('.')[0]

                #Set location of unzipped folder
                unzipped_ext = os.path.join(unzip_dir,file_name)

                #For all files,including sub dirs, in the unzipped folder
                for dirpath, dirnames, filenames in os.walk(unzipped_ext):
                    for filename in filenames:
                        #If the file is javascript
                        if filename.endswith(".js"):
                            output_dir = os.path.join(ast_dir,file_name)
                            create_directory(output_dir)
                            #Set filepath
                            filepath = os.path.join(dirpath, filename)
                            if(verbose):
                                pbar.write("Generating AST for file: %s" %filepath)
                            command = 'esparse "'+filepath+'" '
                            try:
                                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                                result = result.stdout

                                #TODO: Need to check if file exists 
                                if os.path.isfile(os.path.join(output_dir,filename.split(".")[0]+".json")):
                                    i = 1
                                    while os.path.isfile(os.path.join(output_dir,filename.split(".")[0]+'_'+str(i)+".json")):
                                        i += 1
                                    
                                    with open(os.path.join(output_dir,filename.split(".")[0]+'_'+str(i)+".json"), 'w') as file:
                                        file.write(result)
                                else:
                                    with open(os.path.join(output_dir,filename.split(".")[0]+".json"), 'w') as file:
                                        file.write(result)
                                
                            except Exception as e:
                                with open("Error AST.txt", 'a') as file:
                                    file.write(f"Error with file {filepath} \n")
                                    file.write(str(e))
                                    file.write("\n\n")
            pbar.update(1)

