# Security and privacy of Accessible Web Extensions

This repo downloads, unpacks, and analyses web extensions looking at their security and privacy.

## Installation

### Pre-requisites
* NPM
    * [js-beautify](https://www.npmjs.com/package/js-beautify) installed globally
    * [esprima](https://github.com/jquery/esprima) 

Install requirements

```bash 
python -m pip install -r requirements.txt
 ```


## 1. Get a list of extensions
First we need to get a list of extensions. This is done using the console in a web browser, by finding the relevant extensions on the Google Store. We then get the URL of each extension by running the scrip "get_extension_urls.js" in the developer console and saving the results to a txt file. Need to set profile which is already logged in, for some extensions which include "mature content". Currently this list needs to not include extra info after the actual link, having info such as `?hl` will cause the script to crash

## 2. Downloading extensions
Next, we need to download the crx files for each extension. While doing this, the script will also gather data about each extension, such as name, developer, rating, number of downloads, etc. This can be done using the script "download_extensions.py", example: 
```bash 
python3 download_extensions.py <file.txt>

# See below command for full details
python3 download_extension.py -h
```

## 3. Preprocessing
After this, we need to process the crx files ready for analysis. We start by extracting them, which takes them from crx to normal folders. After this we try to
deobfuscate and beautify where possible using JS Beautify. To run:
```bash 
python3 preprocess.py <file.csv>
#See below for full details
python 3 download_extension.py -h
```

## 4. Get info from manifest
We then get permissions, manifest version and hosts and output them into two csv files.
```bash 
python3 get_manifest.py <file.csv> 
```

## 5. Generating ASTs
We can then generate AST using Esprima
```bash
python3 get_asts.py <file.csv>
```

