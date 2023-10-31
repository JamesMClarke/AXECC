// Instantiating new EasyHTTP class
const http = new EasyHTTP;
const urls = []
// User Data
chrome.tabs.query({windowId: chrome.windows.WINDOW_ID_CURRENT}, (tabs) => {
    document.write(`<h3>The tabs you're on are:</h3>`);
    document.write('<ul>');
    for (let i = 0; i < tabs.length; i++) {
      document.write(`<li>${tabs[i].url}</li>`);
      urls.push(tabs[i].url)
    }
    document.write('</ul>');
    window.alert(urls)
    
    const data = {
        name: 'sunny yadav',
        username: 'sunnyyadav',
        email: 'sunny@gmail.com',
        url: urls
    }

    // Update Post
    http.put(
    'http://localhost:8080/',
        data)

    // Resolving promise for response data
    .then(data => console.log(data))

    // Resolving promise for error
    .catch(err => console.log(err));
  });

