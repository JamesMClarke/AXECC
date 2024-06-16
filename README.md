# Security and privacy of Accessible Web Extensions

This repo downloads, unpacks, and analyses web extensions looking at their security and privacy.

## Installation

### Pre-requisites
* Node
  * NPM
    * [js-beautify](https://www.npmjs.com/package/js-beautify) installed globally
    * [esprima](https://github.com/jquery/esprima)

* Python 3.12
  * Conda
  * environment.yaml
  
* Other
  * Docker 
  
## Basics
All files will are saved to the ```extensions\<name_of_txt>``` folder.

## 1. Get a list of extensions
First we need to get a list of extensions. This can be done using the following get_urls.mjs, all it needs the url you want to get the urls from for example https://chromewebstore.google.com/search/example.
```bash
# For a search
node get_urls.mjs <url> <file_name>

#For a category
node get_urls.mjs -c <url> <file_name>
```

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
python3 preprocess.py <file.sqlite>
#See below for full details
python 3 preprocess.py -h
```

## 4. Get info from manifest
We then get permissions, manifest version and hosts and output them into two csv files.
```bash 
python3 get_manifest.py <file.sqlite> 
```

## 5. Running crawl
We can run a crawl of a test site using all extensions, doing this records the HTML of the page, the network traffic while visiting it using [mitmproxy](https://mitmproxy.org/), [VisualV8](https://github.com/wspr-ncsu/visiblev8/tree/master) logs, the accessibility tree, WAVE and Google Lighthouse results.
```bash
# Run the crawl
python3 run_crawl.py <file.sqlite> <time in seconds> 
```

## 7. Post Processing
We can now run our post-processor, we rely on [VisableV8's post processor](https://github.com/wspr-ncsu/visiblev8/tree/master/post-processor) to format VisableV8's results

```bash
# Change directory to post process
cd post-processor
# Run post processor
python3 postProcess.py ../extensions/folder/file.sqlite
```
## n. Generating ASTs
We can then generate AST using Esprima
```bash
python3 get_asts.py <file.csv>

