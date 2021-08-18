async function fetchFrom(url){ //Raihan142857
    return await (await fetch(`https://cors.9gr.repl.co/${url}`)).json(); //9gr
}

document.head = document.head || document.getElementsByTagName('head')[0];

let body_content = ``

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


function redirect(url){
    window.location = url;
}

function button_submit(){
    console.log(123231);
    let _form = document.getElementById("search");
    console.log(_form);
    //Move to the page where the project is.
    redirect(`index.html?pid=${_form.value}`);
}

function is_acceptable_link(link){
    let whitelist = ['assets.scratch.mit.edu', 'cdn2.scratch.mit.edu'];
    if(whitelist.indexOf(link.split('//')[1].split('/')[0]) >= 0){
        return true
    }else{
        return false
    }
}

async function renderElement(_name, perameters, _LastBlock){
    const name = _name.split(" %s")[0];
    console.log(name);
    //Check if the tag is valid and if it is render it with all accociated perameters being met.
    if(name == "Add text"){
        body_content += `<span style="font-size:${perameters[1]}px">${perameters[0]}</span>`;
    }else if(name == "Add image"){
        if(is_acceptable_link(perameters[0])){
            body_content += `<img src=${perameters[0]}>`
        }else{
            //Load in an error templace.
        }
    }else if(name == "Break"){
        body_content += "<br>"
    }else if(name == "Set icon"){
        if(is_acceptable_link(perameters[0])){
            changeFavicon(perameters[0]);
        }else{
            //Load in an error templace.
        }
    }else if(name == "Embed project"){
        project = await fetchFrom(`api.scratch.mit.edu/projects/${perameters[0]}`);
        user = project.author.username;
        console.log(user);

        body_content += `
        <div class="embed-credit">
        Huge thanks to ${user} for the amazing project.
        <br>
        <iframe src="https://scratch.mit.edu/projects/${perameters[0]}/embed" allowtransparency="true" width="485" height="402" frameborder="0" scrolling="no" allowfullscreen></iframe>
        </div>
        `;
    }else if(name == "Div"){
        body_content += `<div class="${perameters[0]}" id="${perameters[1]}">`;
    }else if(name == "End"){
        if(_LastBlock == "Div"){
            body_content += "</div>";
        }
    }
}

let NotFoundPage = `
<link rel="stylesheet" type="text/css"href="scratchWeb.css">
<div class="Main_text">HTTP: 404 ERROR</div>
<img src="404Logo.png" alt="404 image" width=360 height=360 class="image">
<div class="description">It seems there is not a ScratchWeb page here</div>
`;

async function main(){
    //Load the div element to write HTML code to.
    div = document.getElementById('content');

    //Get the pid url peram
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    
    //If there is not a url perameter then render homepage
    if(!(urlParams.get('pid'))){
        div.innerHTML = `
        <div class="homepage">
        <link rel="stylesheet" type="text/css"href="scratchWeb.css">
        <div class="search-container">
        <img src=ScratchWeb.png class="banner">
          <form>
              <input type="text" placeholder="Search for a project ID" id="search">
              <button type=button onClick="button_submit()" id="button">Submit</button>
              
          </form>
        </div>
        </div>
        `
        return;
    }else{
        //A powered by scratch web image should be rendered in the top right hand corner.
    }

    project = await fetchFrom(`projects.scratch.mit.edu/${urlParams.get('pid')}`);

    //Check to see if the project is actually shared on scratch
    
    let scratchApiProject = await fetchFrom(`api.scratch.mit.edu/projects/${urlParams.get('pid')}`);
    try{
        let creator = scratchApiProject.author.username;
    }catch(err){
        //If it's not shared show error page (allowing unshared projects causes moderation issues)
        div.innerHTML = NotFoundPage;
        return;
    }
    document.title = scratchApiProject.title;

    //Get a list of all the blocks in the project
    const blocks = project.targets[0].blocks;

    //Create a last block variable to add support for the nesting of elements within each other
    let lastBlock = null;
    
    for (let prop in blocks) {
        //Loop through all blocks in the project
        if (Object.prototype.hasOwnProperty.call(blocks, prop)) {
            if(blocks[prop].opcode == "procedures_call"){
                //Pasrse out the inputs and the name of the block
                let inputs = blocks[prop].inputs;
                let blockName = blocks[prop].mutation.proccode;
                if(["Div", "Span", "List"].includes(blockName.split(" %s")[0])){
                    lastBlock = blockName.split(" %s")[0];
                }
                let input_array = []
                for(let inp in inputs){
                    if(Object.prototype.hasOwnProperty.call(inputs, inp)){
                        input_array.push(inputs[inp][1][1]);
                    }
                }
                renderElement(blockName, input_array, lastBlock);
            }
        }
    }

    div.innerHTML = body_content;
}

onload = main();