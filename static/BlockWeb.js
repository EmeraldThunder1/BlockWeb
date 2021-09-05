function button_submit(){
    window.location = `/projects/${document.getElementById("search").value}`
}

function changeFavicon(src) { //https://stackoverflow.com/questions/260857/changing-website-favicon-dynamically
    console.log('Changing')
    var link = document.createElement('link'),
    oldLink = document.getElementById('dynamic-favicon');
    link.id = 'dynamic-favicon';
    link.rel = 'shortcut icon';
    link.href = src;
    if (oldLink) {
        document.head.removeChild(oldLink);
    }
    document.head.appendChild(link);
}