import path from "path";
import sqlite3 from "sqlite3";
import {
    program
} from 'commander';
import {
    exit
} from 'process';

import fs from 'fs-extra';

import config from './custom-config.mjs';
import async from 'async';
import lighthouse from 'lighthouse';

// Just use normal puppeteer
import puppeteer from 'puppeteer';
// Or add stealth plugin and use defaults (all evasion techniques)
// import puppeteer from 'puppeteer-extra';
// import StealthPlugin from 'puppeteer-extra-plugin-stealth';
// puppeteer.use(StealthPlugin());


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

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
                const selectNameAndFile = `SELECT name, file FROM extensions ORDER BY id`;

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

                    const createTableRequests = `CREATE TABLE IF NOT EXISTS current_ext (
id INTEGER PRIMARY KEY AUTOINCREMENT,
extension TEXT
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
waveAria INT,
time FLOAT
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

async function checkCurrentExt(extension) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(sqlFile, (err) => {
            if (err) {
                return reject(new Error(`Error connecting to database: ${err}`));
            }

            const query = "SELECT * FROM current_ext WHERE extension = ?";
            db.all(query, [extension], (err, rows) => {
                db.close((closeErr) => { // Close connection even on errors
                    if (closeErr) {
                        console.error('Error closing database connection:', closeErr);
                    }

                    if (err) {
                        return false;
                    }

                    resolve(rows.length > 0); // Check if at least one row exists
                });
            });
        });
    });
}

async function updateCurrentExt(extension) {
    const db = new sqlite3.Database(sqlFile, (err) => {
        if (err) {
            reject(err);
        } else {
            const query = `UPDATE current_ext SET extension = ? where id = 1`;

            db.run(query, [extension], (err) => {
                if (err) {
                    console.error(err.message);
                    console.log("Error");
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

async function setCurrentExt(extension) {
    const db = new sqlite3.Database(sqlFile);
    let attempt = 1;

    const retryOpts = {
        times: 3, // Retry maximum 3 times
        interval: (attempt) => Math.min(2000, 2 * attempt * 1000), // Exponential backoff with a 2s cap
    };

    async.retry(retryOpts, (callback) => {
        const query = `INSERT INTO current_ext (extension) VALUES (?);`;
        db.run(query, [extension], (err) => {
            if (err) {
                console.error(err.message);
                console.log(`Error setting extension, retrying... (attempt: ${retryOpts.times - attempt})`);
                return callback(err);
            }
            callback(); // No error, operation successful
        });
    }, (err) => {
        if (err) {
            console.error('Failed to set current extension after retries');
            // Handle overall failure here (e.g., log error or throw an exception)
        } else {
            console.log('Extension set successfully');
        }
        db.close((err) => {
            // Handle database close error if needed
        });
    });
}


function addCrawl(extension, success, lighthouseScore, wave, crawlTime) {
    const db = new sqlite3.Database(sqlFile, (err) => {
        if (err) {
            reject(err);
        } else {
            const query = `INSERT INTO crawl (extension, success, lighthouse, waveErrors,waveContrastErrors,waveAlerts, waveFeatures, waveStructuralElements, waveAria, time ) VALUES (?,?,?,?,?,?,?,?,?,?)`;

            db.run(query, [extension, success, lighthouseScore, wave.statistics.error, wave.statistics.contrast, wave.statistics.alert, wave.statistics.feature, wave.statistics.structure, wave.statistics.aria, crawlTime], (err) => {
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

async function gotoPageWithRetry(page, url, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            await page.goto(url, {
                waitUntil: 'networkidle2',
                timeout: 60000 // Increase timeout to 60 seconds
            });
            return;
        } catch (error) {
            console.error(`Error navigating to ${url}: ${error.message}`);
            if (i === retries - 1) throw error; // Rethrow error after final attempt
            console.log(`Retrying... (${i + 1}/${retries})`);
        }
    }
}

async function runLighthouse(url, config, page) {
    try {
        await page.setBypassCSP(true);
        await page.setCacheEnabled(false);
        
        // Add timeout and retry logic
        const maxRetries = 3;
        let attempt = 0;
        
        while (attempt < maxRetries) {
            try {
                const { lhr } = await lighthouse(url, undefined, config, page);
                console.log(`Lighthouse score: ${lhr.categories.accessibility.score}`);
                return lhr;
            } catch (error) {
                attempt++;
                if (attempt === maxRetries) {
                    console.error(`Failed to run Lighthouse after ${maxRetries} attempts:`, error);
                    throw error;
                }
                console.log(`Lighthouse attempt ${attempt} failed, retrying...`);
                await delay(2000); // Wait 2 seconds before retrying
            }
        }
    } catch (error) {
        console.error("Lighthouse error:", error);
        return {
            categories: {
                accessibility: {
                    score: -1
                }
            }
        };
    }
}

async function crawl(extension) {
    let extension_output = path.join(outputDir, extension)
    create_dir(extension_output);
    const time_delay = 2000;
    let browser;
    try {
    if (extension === 'baseline') {
        await setCurrentExt(extension);
        await delay(time_delay);
        browser = await puppeteer.launch({
            executablePath: '/opt/chromium.org/chromium/chrome',
            headless: true,
            ignoreHTTPSErrors: true,
            ignoreDefaultArgs: ['--enable-automation'],
            userDataDir: './tmp',
            args: [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        const version = await browser.version();
        console.log(`Chrome Version: ${version}`);
    } else {
        await updateCurrentExt(extension);
        await delay(time_delay);
        let lastDotIndex = extension.lastIndexOf('.');
        let fileNameWithoutExtension = extension.substring(0, lastDotIndex);
        let extPath = path.join(extensionDir, fileNameWithoutExtension);
        console.log("Extension Path: " + extPath);
        browser = await puppeteer.launch({
            executablePath: '/opt/chromium.org/chromium/chrome',
            headless: true,
            ignoreHTTPSErrors: true,
            ignoreDefaultArgs: ['--enable-automation'],
            userDataDir: './tmp',
            logLevel: 'info',
            args: ['--no-sandbox', `--disable-extensions-except=${extPath}`, `--load-extension=${extPath}`,'--disable-dev-shm-usage','--disable-gpu','--ignore-certificate-errors']
        });
    }
    //Time delay before starting to crawl
        const crawlStart = performance.now();
        const page = await browser.newPage();
        await gotoPageWithRetry(page, url);
        //Allow page to load
        await delay(5000);
        const delayFinished = performance.now();

        const lighthouseStart = performance.now();
        await page.bringToFront();

        var lhr;
        //Run lighthouse
        try{
            lhr = await runLighthouse(url, config, page);
        } catch (error) {
            console.error('Failed to run Lighthouse:', error);
            lhr = {
                categories: {
                    accessibility: {
                        score: -1
                    }
                }
            };
        }


        const lighthouseEnd = performance.now();

        const waveStart = performance.now();
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
        await page.addScriptTag({
            content: waveScript
        });
        let waveStats = {
            statistics: {
                error: 0,
                contrast: 0,
                alert: 0,
                feature: 0,
                structure: 0,
                aria: 0
            }
        };
        if (typeof responseObject[0] === 'string') {
            try {
                waveStats = JSON.parse(responseObject[0]);
            } catch (parseError) {
                console.error('Failed to parse waveStats:', parseError);
                waveStats = {
                    statistics: {
                        error: -1,
                        contrast: -1,
                        alert: -1,
                        feature: -1,
                        structure: -1,
                        aria: -1
                    }
                };
            }
        } else {
            console.error('Invalid response format for waveStats:', responseObject[0]);
            waveStats = {
                statistics: {
                    error: -1,
                    contrast: -1,
                    alert: -1,
                    feature: -1,
                    structure: -1,
                    aria: -1
                }
            };
        }
        const waveEnd = performance.now();


        // Work out if it needs extra delay
        const currentVisitTime = performance.now() - crawlStart;
        if (currentVisitTime < visitTime) {
            await delay(visitTime - currentVisitTime);
            console.log(`The delay should be ${visitTime - currentVisitTime}`);
        }

        // Screenshot and get html of page
        //await page.screenshot({ 
        //    path: path.join(extension_output, "screenshot.png"), 
        //    type: 'png', 
        //    fullPage: true
        //});
        
        const htmlStart = performance.now();
        const htmlContent = await page.content();
        await fs.promises.writeFile(path.join(extension_output, 'page.html'), htmlContent);
        const htmlFinish = performance.now();

        let localStorage;
        try {
            localStorage = await getAllLocalStorage(page);
        } catch (error) {
            console.error('Failed to get localStorage:', error);
            localStorage = {};
        }
        const serializedLocalStorage = JSON.stringify(localStorage);
        try {
            await saveJsonToFile(serializedLocalStorage, path.join(extension_output, 'localstorage.json'));
        } catch (error) {
            console.error('Failed to save localStorage to file:', error);
        }
        
        let sessionStorage;
        try {
            sessionStorage = await getAllSessionStorage(page);
        } catch (error) {
            console.error('Failed to get sessionStorage:', error);
            sessionStorage = {};
        }
        const serializedSessionStorage = JSON.stringify(sessionStorage);
        try {
            await saveJsonToFile(serializedSessionStorage, path.join(extension_output, 'sessionStorage.json'));
        } catch (error) {
            console.error('Failed to save sessionStorage to file:', error);
        }

        let cookies;
        try {
            cookies = await page.cookies();
            for (let i = 0; i < cookies.length; i++) {
                addCookies(extension, cookies[i]);
            }
        } catch (error) {
            console.error('Failed to get cookies:', error);
            cookies = [];
        }

        const accessibilitySnapshot = await page.accessibility.snapshot();
        await saveJsonToFile(accessibilitySnapshot, path.join(extension_output, 'accessibilitySnapshot.json'));
        moveFiles("vv8", extension_output);
        const crawlEnd = performance.now();

        const crawlLength = crawlEnd - crawlStart;
        console.log(`The crawl took ${crawlLength} ms`);
        addCrawl(extension, 1, lhr.categories.accessibility.score, waveStats, crawlLength);

        if(verbose){
            console.log(`It the delay lasted ${delayFinished - crawlStart} ms`);
            console.log(`Saving the html took ${htmlFinish - htmlStart} ms`);
            console.log(`Lighthouse took ${lighthouseEnd - lighthouseStart} ms`);
            console.log(`WAVE took ${waveEnd - waveStart} ms`);  
        }

        page.on('error', (error) => {
            console.error('Page error:', error);
        });

        page.on('pageerror', (pageError) => {
            console.error('Page error:', pageError);
        });
    } catch (error) {
        console.log(error);

        let wave = {
            statistics: {
                error: -1,
                contrast: -1,
                alert: -1,
                feature: -1,
                structure: -1,
                aria: -1
            }
        };
        addCrawl(extension, 0, -1, wave, 0);
    } finally {
        try {
            await browser.close();
        } catch {
            console.log("Error closing the browser");
        }
    }

}

async function runCrawls(extensions) {
    fs.copyFile('/artifacts/idldata.json', path.join(outputDir, 'idldata.json'), (err) => {
        if (err) {
            console.error('Error copying file:', err);
        } else {
            console.log('File copied successfully!');
        }
    });

    await crawl('baseline');
    fs.rmSync(path.join(currentDir, 'tmp'), {
        recursive: true,
        force: true
    });

    for (const extension of extensions) {
        // Call crawl function directly without await (it's already async)
        try {
            if (extensions.file != 'None') {
                await crawl(extension.file);
                fs.rmSync(path.join(currentDir, 'tmp'), {
                    recursive: true,
                    force: true
                });
            }
        } catch (error) {
            // Handling the error
            console.error("An error occurred with the crawl:", error);
            let wave = {
                statistics: {
                    error: -1,
                    contrast: -1,
                    alert: -1,
                    feature: -1,
                    structure: -1,
                    aria: -1
                }
            };
            addCrawl(extension, 0, -1, wave, 0);
            continue; // Continue to the next extension
        }
    }
}


program
    .version('0.0.1')
    .description('Visit webpage using extension and process data')
    .argument('<sql>', 'Input sqlite file to be processed')
    .argument('<time>', 'Time to visit site with each extension (mili-seconds)', parseInt)
    .option('-v, --verbose', 'Output verbose information')
    .option('--login_page <customString>', 'Use the inaccessible login page as the honeypage')
    .option('--wordpress <customString>', 'Use the wordpress page as the honeypage with a custom string');

program.parse();

// Validate mutually exclusive options
const options = program.opts();
if (options.login_page && options.wordpress) {
    console.error('Error: --login_page and --wordpress cannot be used together');
    process.exit(1);
}

// Set default page type if none specified
const pageType = options.login_page ? 'login-page' : 
                 options.wordpress ? 'wordpress' : 
                 'login-page'; // default to login-page

// Update the URL based on page type
const url = pageType === 'login-page' 
    ? 'http://web_server' 
    : 'http://web_server' + options.wordpress.replace(/^'|'$/g, '');

const sqlFile = program.args[0];
const visitTime = program.args[1];

const verbose = program.verbose || options.verbose || options.v;

// Your program logic using csvFile, visitTime, and verbose

console.log(`Processing SQLite file: ${sqlFile}`);
console.log(`Visit time per extension: ${visitTime} ms`);
console.log(`Verbose mode: ${verbose}`);
console.log(`Visiting the following url: ${url}`)

const currentDir = process.cwd();
const extensionDir = path.join(path.dirname(sqlFile), 'preprocessed');
const outputDir = path.join(path.dirname(sqlFile), 'crawl');
create_dir(outputDir)

getExtensions()
    .then((extensions) => {
        runCrawls(extensions);
    })
