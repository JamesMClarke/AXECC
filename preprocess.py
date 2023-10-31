from pathlib import Path
import os, argparse, sys, csv, zipfile
from tqdm import tqdm
from time import sleep

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

current_dir = os.getcwd()

#Create preprocessing dir
create_directory(os.path.join(current_dir,"preprocessing"))

#TODO: Add the ablity to include multiple folders
#Take input of csv file
parser = argparse.ArgumentParser("Preprocess extenions")
parser.add_argument("csv", help="Input the name of the csv file to be processed.", type=str)
args = parser.parse_args()
csv_name = args.csv

#Check if csv file exists
csv_file = os.path.join(current_dir,csv_name+".csv")
if(os.path.isfile(csv_file)):
    print("File %s exists, starting preprocessing" %(csv_name))
else:
    print("File %s doesn't exists, stopping" %(csv_file))
    sys.exit()


#Create folder for files to be unzipped into
unzip_dir = os.path.join(current_dir,"preprocessing",csv_name+"_unzipped")
create_directory(unzip_dir)
print("Unzipping all crx files into folder: %s" %(unzip_dir))

#Set dir for crx files
crx_dir = os.path.join(current_dir,"crx_files",csv_name)

#Unzip all crxs in csv file
errors = 0
with open(csv_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    #TODO: Check that I need to remove the first row, as I think this may get added later
    rows.pop(0)
    no_rows = len(rows)
    with tqdm(total=no_rows) as pbar:
        for row in rows:
            file = row[7]
            if(os.path.isdir(os.path.join(unzip_dir, file))):
                print(file)
            #TODO: Add check for if file exists
            try:
                with zipfile.ZipFile(os.path.join(crx_dir,file), 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(unzip_dir,file.split('.')[0]))
            except:
                errors += 1
                errors_file = open('Error Unzip.csv', 'a', encoding='utf-8')
                errors_file.write(row[0]+row[1]+file+'\n')
                errors_file.close()
            pbar.update(1)

if errors != 0:
    print("%s files couldn't be unzipped, see Error Unzip.csv for details"%(errors))

files_in_dir = len([d for d in os.listdir(unzip_dir) if os.path.isdir(os.path.join(unzip_dir, d))])

if no_rows < files_in_dir:
    print("More")
    print("There are %s in the csv file" % no_rows)
    print("%s files have been unzipped" % files_in_dir)
elif no_rows > files_in_dir:
    print("Some files have not been unzipped")
    print("There are %s in the csv file" % no_rows)
    print("%s files have been unzipped" % files_in_dir)
else:
    print("Finished unzipping sucessfully")
#TODO: Add check that all files have been unzipped

#TODO: Need to apply obfuscation and minification