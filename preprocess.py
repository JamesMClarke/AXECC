from pathlib import Path
import os, argparse, sys, csv, zipfile

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

current_dir = os.getcwd()

#Create preprocessing dir
create_directory(os.path.join(current_dir,"preprocessing"))

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
with open(csv_file, 'r') as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        try:
            with zipfile.ZipFile(os.path.join(crx_dir,row[7]), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(unzip_dir,row[7].split('.')[0]))
        except:
                errors_file = open('Error Unzip.txt', 'a', encoding='utf-8')
                errors_file.write(row[7]+'\n')
                errors_file.close()

print("Finished unzipping")

#TODO: Need to apply obfuscation and minification