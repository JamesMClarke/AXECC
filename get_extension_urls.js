var r = document.getElementsByTagName("a");
//var p=0;
for (i=0;i<r.length;i++){
    if (r[i].href.includes("https://chrome.google.com/webstore/detail/")){
    	console.log(r[i].href);
    	//p++;
    }
}

//console.log(p);