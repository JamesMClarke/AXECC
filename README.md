# Security and privacy of Accessible Web Extensions

This repo downloads, unpacks, and anaylises web extensions looking at their security and privacy.

## 1. Get a list of extenions
First we need to get a list of extenions. This is done using the console in a web browser, by finding the relevent extensions on the Google Store. We then get the URL of each extension by running the scrip "get_extension_urls.js" in the developer console and saving the results to a txt file. Need to set profile which is already logged in, for some extensions which include "mature content".

## 2. Downloading extensions
Next, we need to download the crx files for each extension. This can be done using the script "download_extensions.py", and supplying it with the relevent file from above. While doing this, the script will also gather data about each extension, such as name, developer, rating, number of downloads, etc.

## 3. Preprocessing
After this, we need to process the crx files ready for analysis. We start by extracting them, which takes them from crx to normal folders. After this we try to
deobfuscated and deminified where possible using JS Beautify.

