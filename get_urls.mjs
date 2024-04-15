import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { program } from 'commander';

var category = false

 async function clickLoadMoreButton(page) {
   if (!category){
     console.log("Not cat")
     const button = await page.waitForSelector('button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf.Zg3Y9'); // More specific selector
     await button.click();
   } else {
     const button = await page.waitForSelector('button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf'); // More specific selector
     await button.click();

   }
 }

function create_dir(directoryPath){
  try {
    fs.mkdirSync(directoryPath);
    console.log('Directory created successfully!');
  } catch (err) {
    if (err.code === 'EEXIST') {
      console.log('Directory already exists.');
    } else {
      console.error('Error creating directory:', err);
    }
  }
}

program
  .version('0.0.1')  // Set your program version
  .description('Get a list of extension urls based on a search term');

program
  .argument('<url>', 'Input search url to get extension urls from')
  .argument('filename', 'Input the file name to save the urls too')
  .option('-v, --verbose', 'Output verbose information')
  .option('-c, --category', 'Get urls from a category rather than a search');

program.parse();

const url = program.args[0];
const filename = program.args[1];
const verbose = program.verbose;
const options = program.opts();
category = options.c || options.category;
console.log(category);

console.log(`Saving urls found on ${url} to ${filename}`);

const cwd = process.cwd();
const extensions_dir = path.join(cwd, 'extensions');
const output_dir = path.join(extensions_dir, filename);

create_dir(extensions_dir);
create_dir(output_dir);


(async () => {
    const browser2 = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: false
    });

  const page = await browser2.newPage();
  // Navigate to any website to focus on the address bar
  await page.goto(url);
  // Call the function to click the button initially
  await clickLoadMoreButton(page);

  // You can repeat this function in a loop to keep clicking as long as the button exists
  while (true) {
    try {
      await clickLoadMoreButton(page);
    } catch (error) {
     //Break the loop if button not found (optional)
      break;
    }
    // Add a delay between clicks if needed (optional)
    await page.waitForTimeout(1000); // Wait 2 seconds before clicking again
  }

  page.on('console', async (msg) => {
    const msgArgs = msg.args();
    for (let i = 0; i < msgArgs.length; ++i) {
      console.log(await msgArgs[i].jsonValue());
    }
  });

  const script = `
  var r = document.getElementsByTagName("a");
//var p=0;
for (i=0;i<r.length;i++){
    if (r[i].href.includes("detail/")){
    	console.log(r[i].href);
    	//p++;
    }
}`

    const consoleMessages = [];

    // Listen for console messages before running the code
    page.on('console', message => consoleMessages.push(message.text()));

    // Execute the code in the browser context
    await page.evaluate(script);

    // Stop listening for console messages
    page.removeAllListeners('console');

  const content = consoleMessages.join('\n'); // Join array elements with newline character
  fs.writeFile(path.join(output_dir, filename)+".txt", content, 'utf8', (err) => {
    if (err) {
      console.error('Error writing to file:', err);
    } else {
      console.log(`Successfully wrote ${consoleMessages.length} items to ${filename}`);
    }
  });

  // Your automation code here to interact with the extension

  // Close the browser when done
  //await browser2.close();


})();
