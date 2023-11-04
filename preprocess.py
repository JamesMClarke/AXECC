from pathlib import Path
import os, argparse, sys, csv, zipfile, jsbeautifier, cssbeautifier, _thread
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
parser = argparse.ArgumentParser("Preprocess extensions")
parser.add_argument("csv", help="Input the name of the csv file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
csv_file = args.csv
verbose = args.verbose

csv_name = os.path.basename(csv_file).split(".")[0]

#Check if csv file exists
csv_file = os.path.join(current_dir,csv_file)
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
unzipped = 0
with open(csv_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    no_rows = len(rows)
    with tqdm(total=no_rows) as pbar:
        for row in rows:
            file = row[7]\
            #Checks if there is a file to unzip
            if(os.path.isfile(os.path.join(crx_dir, file))):
                #Check if folder already exists
                if(os.path.isdir(os.path.join(unzip_dir, file.split('.')[0]))):
                    if verbose:
                        tqdm.write("Folder already exists")
                        tqdm.write(file)
                        tqdm.write(row[1])
                
                #Try to unzip file
                try:
                    with zipfile.ZipFile(os.path.join(crx_dir,file), 'r') as zip_ref:
                        unzipped += 1
                        zip_ref.extractall(os.path.join(unzip_dir,file.split('.')[0]))
                except Exception as e :
                    if verbose:
                        tqdm.write("Error unzipping %s"%file)
                    errors += 1
                    errors_file = open('Error Unzip.csv', 'a', encoding='utf-8')
                    errors_file.write(row[0]+row[1]+file+str(e)+'\n')
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

#Create dir for de-obfuscation and de-minification
de_dir = os.path.join(current_dir,"preprocessing",csv_name+"_de")
create_directory(de_dir)

with open(csv_file, 'r') as csvfile:
    with tqdm(total=no_rows) as pbar:
        for row in rows:
            #Get filename and remove .crx
            file = row[7]
            if file != "error":
                file_name = file.split('.')[0]

                #Set location of uzipped folder
                unzipped_ext = os.path.join(unzip_dir,file_name)

                #Set output location and create folder
                output_dir = os.path.join(de_dir, file_name)
                create_directory(output_dir)

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
                                        try:
                                            css = cssbeautifier.beautify_file(filepath)
                                            res = jsbeautifier.beautify(css)
                                        except:
                                            res = jsbeautifier.beautify_file(filepath)
                                        
                                        #Check if file already exists
                                        if not os.path.isfile(os.path.join(output_dir, filename)):
                                            #Write output to file in file_de, in a folder called what the extension is called
                                            with open(os.path.join(output_dir, filename), 'w') as f:
                                                # Write to the file
                                                f.write(res)
                                        else:
                                            i = 1
                                            without_ext, ext = os.path.splitext(filename)
                                            if verbose:
                                                tqdm.write("File %s %s already exists, creating new file"%(without_ext,ext))

                                            while os.path.isfile(os.path.join(output_dir,without_ext+'_'+str(i)+ext)):
                                                i += 1
                                            
                                            with open(os.path.join(output_dir,without_ext+'_'+str(i)+ext), 'w') as f:
                                                # Write to the file
                                                f.write(res)
                                            break
                                            
                                    except Exception as e:
                                        if attempt == 4:  # This is the last attempt
                                            tqdm.write(filepath+" couldn't be saved")
                                            errors_file = open('Error URL.txt', 'a', encoding='utf-8')
                                            errors_file.write(filepath + " "+ str(e)+'\n')
                                            errors_file.close()
                                            raise  # Re-raise the last exception

                            
            pbar.update(1)