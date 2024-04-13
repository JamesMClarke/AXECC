import puppeteer from 'puppeteer-extra';
import path from "path";
//import fs from "fs";
import sqlite3 from "sqlite3";
import {
    program
} from 'commander';
import {
    exit
} from 'process';

import fs from 'fs-extra';

import config from './custom-config.mjs';

// add stealth plugin and use defaults (all evasion techniques)
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import lighthouse from 'lighthouse';
puppeteer.use(StealthPlugin());


async function getAllLocalStorage(page) {
    const localStorageObj = await page.evaluate(() => {
        const storage = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            storage[key] = localStorage.getItem(key);
        }
        return storage;
    });
    return localStorageObj;
}

async function getAllSessionStorage(page) {
    const localStorageObj = await page.evaluate(() => {
        const storage = {};
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            storage[key] = sessionStorage.getItem(key);
        }
        return storage;
    });
    return localStorageObj;
}

async function saveJsonToFile(myObject, filename) {
    // Convert the object to a JSON string
    const jsonData = JSON.stringify(myObject, null, 2); // Include indentation for readability (optional)

    // Write the JSON data to a file
    fs.writeFile(filename, jsonData, (err) => {
        if (verbose) {
            if (err) {
                console.error(err);
            } else {
                console.log('Data saved successfully to data.json');
            }
        }
    });
}

function delay(time) {
    return new Promise(function(resolve) {
        setTimeout(resolve, time)
    });
}

function create_dir(directoryPath) {
    try {
        fs.mkdirSync(directoryPath);
    } catch (err) {
        if (verbose) {
            if (err.code === 'EEXIST') {
                console.log('Directory already exists.');
            } else {
                console.error('Error creating directory:', err);
            }
        }
    }
}

function moveFiles(pattern, destDir) {
  const files = fs.readdirSync(currentDir).filter(file => file.startsWith(pattern));

  for (const file of files) {
    const oldPath = `${currentDir}/${file}`;
    const newPath = `${destDir}/${file}`;

    try {
      fs.move(oldPath, newPath);
      if (verbose) {
        console.log(`Successfully moved ${file} to ${destDir}`);
      }
    } catch (err) {
      if (verbose) {
        console.error(`Error moving ${file}: ${err.message}`);
      }
    }
  }
}

function getExtensions() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(sqlFile, (err) => {
            if (err) {
                reject(err);
            } else {
                const selectNameAndFile = `SELECT name, file FROM extensions`;

                db.all(selectNameAndFile, [], (err, rows) => {
                    if (err) {
                        reject(err);
                        //TODO Handle table not found
                    } else {
                        resolve(rows); // Resolve the promise with the results
                    }

                    const createTableQuery = `CREATE TABLE IF NOT EXISTS cookies (
  cookieId INTEGER PRIMARY KEY AUTOINCREMENT,
  extension TEXT,
  name TEXT ,
  value TEXT,
  domain TEXT,
  path TEXT,
  expires INTEGER,
  size INTEGER
)`;

                    db.run(createTableQuery, (err) => {
                        if (verbose) {
                            if (err) {
                                console.error(err.message);
                            } else {
                                console.log('Cookies table created (if it did not exist).');
                            }
                        }
                    });

                    const createTableRequests = `CREATE TABLE IF NOT EXISTS requests (
requestId INTEGER PRIMARY KEY AUTOINCREMENT,
extension TEXT,
url TEXT,
requestHeaders TEXT,
responseHeaders TEXT,
status TEXT,
interceptionId TEXT,
requestIdNew TEXT,
timestamp TEXT,
method TEXT,
redirectChain TEXT,
responseText TEXT
)`;
                 db.run(createTableRequests, (err) => {
                        if (verbose) {
                            if (err) {
                                console.error(err.message);
                            } else {
                                console.log('Requests table created (if it did not exist).');
                            }
                        }
                    });

       const createTableCrawl = `CREATE TABLE IF NOT EXISTS crawl (
crawlId INTEGER PRIMARY KEY AUTOINCREMENT,
extension TEXT,
success INT,
lighthouse INT,
waveErrors INT,
waveContrastErrors INT,
waveAlerts INT,
waveFeatures INT,
waveStructuralElements INT,
waveAria INT
)`;
                 db.run(createTableCrawl, (err) => {
                        if (verbose) {
                            if (err) {
                                console.error(err.message);
                            } else {
                                console.log('Crawl table created (if it did not exist).');
                            }
                        }
                    });

                    db.close(); // Close the database connection even on error
                });
            }
        });
    });
}

function addCookies(extension, cookie) {
    const db = new sqlite3.Database(sqlFile, (err) => {
        if (err) {
            reject(err);
        } else {
            const query = `INSERT INTO cookies (extension, name, value, domain, path, expires, size) VALUES (?, ?, ?, ?,?, ?, ?)`;

            db.run(query, [extension, cookie.name, cookie.value, cookie.domain, cookie.path, cookie.expires, cookie.size], (err) => {
                if (verbose) {
                    if (err) {
                        console.error(err.message);
                        console.log("Error");
                    } else {
                        console.log(`Cookie ${cookie.name} added to database.`);
                    }
                }
            });

        db.close((err) => {
            if (verbose) {
                if (err) {
                    console.error(err.message);
                } else {
                    console.log('Closed the database connection.');
                }
            }
        });
        }
    });
}

async function addRequest(extension, request, response , redirectChain) {
    const db = new sqlite3.Database(sqlFile, (err) => {
        if (err) {
            reject(err);
        } else {


            let chain = request.redirectChain()
            let redirectChain = []

            for (var index = 0; index < chain.length; index ++) {
                redirectChain.push({
                    "url" : chain[index].url(),
                    "interceptionId" : chain[index]._interceptionId,
                    "requestId" : chain[index]._requestId
                })
            }

            //let responseStatus = await response.status()
            let responseStatus = response.status()
            let responseText;

            if (responseStatus == 200) {
                try {
                    //responseText = await response.text()
                    responseText = response.text()
                }
                catch{
                    responseText = ""
                }
            }

            const requestHeaders = JSON.stringify(request.headers());
            const responseHeaders = JSON.stringify(response.headers());
            redirectChain = JSON.stringify(redirectChain);

            const query = `INSERT INTO requests (extension, url, requestHeaders, responseHeaders, status, interceptionId, requestId, timestamp, method, redirectChain, responseText) VALUES (?, ?, ?, ?,?, ?, ?,?,?,?,?)`;

            db.run(query, [extension, request.url(), requestHeaders, responseHeaders, response.status(), request._interceptionId, request._requestId, request.timestamp, request.method(), redirectChain, responseText == ""], (err) => {
                if (verbose) {
                    if (err) {
                        console.error(err.message);
                        console.log("Error");
                    } else {
                        console.log(`Request ${request.url()} added to database.`);
                    }
                }
            });

        db.close((err) => {
            if (verbose) {
                if (err) {
                    console.error(err.message);
                } else {
                    console.log('Closed the database connection.');
                }
            }
        });
        }
    });
}
function addCrawl(extension, success, lighthouseScore, wave) {
    //console.log(lighthouseScore)
    const db = new sqlite3.Database(sqlFile, (err) => {
        if (err) {
            reject(err);
        } else {
            const query = `INSERT INTO crawl (extension, success, lighthouse, waveErrors,waveContrastErrors,waveAlerts, waveFeatures, waveStructuralElements, waveAria ) VALUES (?,?,?,?,?,?,?,?,?)`;

            db.run(query, [extension, success, lighthouseScore, wave.statistics.error, wave.statistics.contrast,  wave.statistics.alert, wave.statistics.feature, wave.statistics.structure, wave.statistics.aria], (err) => {
                if (verbose) {
                    if (err) {
                        console.error(err.message);
                        console.log("Error");
                    } else {
                        console.log(`Crawl ${extension} added to database.`);
                    }
                }
            });

        db.close((err) => {
            if (verbose) {
                if (err) {
                    console.error(err.message);
                } else {
                    console.log('Closed the database connection.');
                }
            }
        });
        }
    });
}


async function crawl(extension) {
    let extension_output = path.join(outputDir, extension)
    create_dir(extension_output);
    let browser;
    if (extension === 'baseline'){
        browser = await puppeteer.launch({
            executablePath: '/opt/chromium.org/chromium/chrome',
            headless: true,
            ignoreHTTPSErrors: true,
            ignoreDefaultArgs: ['--enable-automation'],
            userDataDir: './tmp',
            args: ['--no-sandbox']
            //, 'screenshot'
        });
    }else{
        let lastDotIndex = extension.lastIndexOf('.');
        let fileNameWithoutExtension = extension.substring(0, lastDotIndex);
    let extPath = path.join(extensionDir, fileNameWithoutExtension);
        console.log("Extension Path: "+extPath);
            browser = await puppeteer.launch({
            executablePath: '/opt/chromium.org/chromium/chrome',
            //executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            headless: true,
            ignoreHTTPSErrors: true,
            ignoreDefaultArgs: ['--enable-automation'],
            userDataDir: './tmp',
            args: ['--no-sandbox', `--disable-extensions-except=${extPath}`, `--load-extension=${extPath}`]
            //'screenshot',
        });
    }


    const page = await browser.newPage();

    await page.setRequestInterception(true);

    page.on('request', (request) => {
        request["timestamp"] = (new Date()).getTime()
        request.continue()
    })


    page.on('requestfinished', async (request) => {
        const response = await request.response();
        const responseHeaders = response.headers();
        await addRequest(extension, request, response);
        })
    // Navigate to any website to focus on the address bar
    await page.goto(url);

    await delay(vistTime);

    // Screenshot and get html of page
    await page.screenshot({ path: path.join(extension_output,"screenshot.jpeg"), type: 'jpeg', fullPage: true });
    const htmlContent = await page.content();
    await fs.promises.writeFile(path.join(extension_output, 'page.html'), htmlContent);


    var allStorage = await getAllLocalStorage(page);
    await saveJsonToFile(allStorage, path.join(extension_output, 'localStorage.json'));
    allStorage = await getAllSessionStorage(page);
    await saveJsonToFile(allStorage, path.join(extension_output, 'sessionStorage.json'));

    const cookies = await page.cookies();

    for (let i = 0; i < cookies.length; i++) {
        addCookies(extension, cookies[i]);
    }

    // Get accessibility evaluation
    const {lhr} = await lighthouse(url, undefined, config, page);
    //console.log(lhr.categories.accessibility.score);
    const responseObject = {};
    page.on('console', async (msg) => {
        const msgArgs = msg.args();
        for (let i = 0; i < msgArgs.length; ++i) {
            const responseValue = await msgArgs[i].jsonValue();

            // Conditionally store responses based on message type (optional)
            if (msg.type() === 'log') { // If you want to store only log messages
                responseObject[i] = responseValue;
            } else {
            // Handle other message types if needed
            }
        }
    });
     // Use page.addScriptTag to add the script to the page
    const waveScript = fs.readFileSync(path.join(process.cwd(), 'wave.min.js'), 'utf8');
    await page.addScriptTag({ content: waveScript });
    const waveStats = JSON.parse(responseObject[0]); // Access the first response
    // console.log(waveStats);
    addCrawl(extension, 1, lhr.categories.accessibility.score, waveStats);
     await browser.close();

    moveFiles("vv8", extension_output);
    fs.rmSync(path.join(currentDir, 'tmp'), {
        recursive: true,
        force: true
    });

}

async function runCrawls(extensions) {
    await crawl('baseline');
  for (const extension of extensions) {
    // Call crawl function directly without await (it's already async)
      await crawl(extension.file);
  }
}


program
    .version('0.0.1') // Set your program version
    .description('Visit webpage using extension and process data');

program
    .argument('<sql>', 'Input sqlite file to be processed')
    .argument('<time>', 'Time to visit site with each extension (mili-seconds)', parseInt) // Parse int
    .option('-v, --verbose', 'Output verbose information');

program.parse();

const sqlFile = program.args[0];
const vistTime = program.args[1];

const options = program.opts();
const verbose = program.verbose || options.verbose || options.v;

// Your program logic using csvFile, visitTime, and verbose

console.log(`Processing SQLite file: ${sqlFile}`);
console.log(`Visit time per extension: ${vistTime} ms`);
console.log(`Verbose mode: ${verbose}`);

const url = 'http://web_server';
const currentDir = process.cwd();
const extensionDir = path.join(path.dirname(sqlFile), 'preprocessed');
const outputDir = path.join(path.dirname(sqlFile), 'crawl');
create_dir(outputDir)

getExtensions()
    .then((extensions) => {
        runCrawls(extensions);
    })
