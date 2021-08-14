async function fetchFrom(url){ //Raihan142857
    return await (await fetch(`https://cors.9gr.repl.co/${url}`)).json(); //9gr
}

function renderElement(_name, perameters, element){
    const name = _name.split(" %s")[0];
    console.log(perameters)
    //Load the div element ready for writing
    div = document.getElementById('content');
    //Check if the tag is valid and if it is render it with all accociated perameters being met.
    if(name == "Add text"){
        div.innerHTML += `<span style="font-size:${perameters[1]}px">${perameters[0]}</span>`;
    }else if(name == "Add image"){
        let whitelist = ['assets.scratch.mit.edu', 'cdn2.scratch.mit.edu'];
        if(whitelist.indexOf(perameters[0].split('//')[1].split('/')[0]) >= 0){
            div.innerHTML += `<img src="${perameters[0]}">`;
        }else{
            //I will create an error template here and render that over what has been previously rendered
        }
    }else if(name == "Break"){
        div.innerHTML += "<br>"
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
        ScratchWeb homepage, improvements needed!
        `
        return;
    }

    project = await fetchFrom(`projects.scratch.mit.edu/${urlParams.get('pid')}`);
    //Later I will add a 404 page here if we cannot find the project

    //Check to see if the project is actually shared on scratch
    
    /*let isShared = await fetchFrom(`api.scratch.mit.edu/${urlParams.get('pid')}`);
    if(!(isShared.ok)){
        //If it's not shared show error page (allowing unshared projects causes moderation issues)
        div.innerHTML = NotFoundPage;
        return;
    }*/

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
                lastBlock = blockName
                let input_array = []
                for(let inp in inputs){
                    if(Object.prototype.hasOwnProperty.call(inputs, inp)){
                        input_array.push(inputs[inp][1][1]);
                    }
                }
                renderElement(blockName, input_array, div)
            }
        }
    }
}

onload = main();