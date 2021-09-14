# Import libraries for use in the code
from flask import Flask, render_template
import requests 
import re


# Create the flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Tie the main route to the homePage template
@app.route('/')
def index():
    return render_template('homePage.html')

# Check to see if a link is in the whitelist
def isWhitelisted(url):
    whitelist = ['cdn2.scratch.mit.edu', 'BlockWeb.EmeraldThunder.repl.co', 'assets.scratch.mit.edu', 'scratch.mit.edu']    
    # Is the url domain whitelisted
    if url.split('/')[2] in whitelist:
        return True
    return False

# Function to return the correct HTML based on the blocks found.
def loadBlockMarkup(blockname, blockInputs, stack):
    CSS = False

    # Prevent XXS attacks (not that there's much they'd have to gain)
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleanName = re.sub(cleanr, '', blockname)
    cleanInputs = []

    # Loop through the inputs and clean the tags
    for item in blockInputs:
        cleanInputs.append(re.sub(cleanr, '', item))


    if cleanName == 'set icon':
        if isWhitelisted(cleanInputs[0]):
            # Return the JavaScript function to change the favicon
            return f'<script>changeFavicon("{cleanInputs[0]}");</script>', False, stack
    elif cleanName == 'add text':
        # Return a span with the body of the text inside it
        return f'<span style="font-size:{cleanInputs[1]}px">{cleanInputs[0]}</span>', False, stack
    elif cleanName == 'break':
        # Return a break element
        return '<br>', False, stack
    elif cleanName == 'add image':
        # Insert the image if it is whitelisted
        if isWhitelisted(cleanInputs[0]):
            return f'<img src="{cleanInputs[0]}">', False, stack
        else:
            return '<img src="/static/NotWhitelisted.png">', False, stack
    elif cleanName == 'embed project':
        # Return the i-frane of the embedded project
        username = requests.get(f'https://api.scratch.mit.edu/projects/{cleanInputs[0]}').json()['author']['username']
        return f'''
        <div class="project-embed">
        <span class="credit-box">Credit to <a href="https://scratch.mit.edu/users/{username}/">{username}</a> for the amazing project</span>
        <br>
        <iframe src="https://scratch.mit.edu/projects/{cleanInputs[0]}/embed" allowtransparency="true" width="485" height="402" frameborder="0" scrolling="no" allowfullscreen></iframe>
        </div>
        ''', False, stack
    elif cleanName == 'div':
        # Open the div element
        return f'<div class="{cleanInputs[0]}" id="{cleanInputs[1]}">', False, stack
    elif cleanName == 'end':
        #Pop the last item from the nest stack
        last = stack.pop()

        # Look at the last tag and close it accordingly
        if last == 'div':
            return '</div>', False, stack
        elif last == 'link':
            return '</a>', False, stack
        elif last == 'span':
            return '</span>', False, stack
        elif last == 'p':
            return '</p>', False, stack
        elif last == 'ordered list':
            return '</ol>', False, stack
        elif last == 'unordered list':
            return '</ul>', False, stack
        elif last == 'list item':
            return '</li>', False, stack
        

    elif cleanName == 'link':
        # Return a link element with href set to the url perameter of the block if it is acceptable
        if isWhitelisted(cleanInputs[0]):
            return f'<a href="{cleanInputs[0]}">', False, stack

    elif cleanName == 'span':
        return f'<span class="{cleanInputs[0]}" id="{cleanInputs[1]}">', False, stack

    elif cleanName == 'p':
        return '<p>', False, stack

    elif cleanName == 'style':
        return cleanInputs[0] + ' {' + f'{cleanInputs[1]}: {cleanInputs[2]};' + '}', True, stack

    elif cleanName == 'raw text':
        return cleanInputs[0], False, stack

    elif cleanName == 'list item':
        return '<li>', False, stack
    elif cleanName == 'unordered list':
        return '<ul>', False, stack
    elif cleanName == 'ordered list':
        return f'<ol start="{cleanInputs[0]}">', False, stack

    elif cleanName == 'small':
        return f'<small>{cleanInputs[0]}</small>', False, stack
    
    elif cleanName == 'bold':
        return f'<b>{cleanInputs[0]}</b>', False, stack
    
    elif cleanName == 'emphasis':
        return f'<em>{cleanInputs[0]}</em>', False, stack

    elif cleanName == 'italics':
        return f'<i>{cleanInputs[0]}</i>', False, stack
    elif cleanName == 'underline':
        return f'<u>{cleanInputs[0]}</u>', False, stack
    elif cleanName == 'centre':
        return f'<center>{cleanInputs[0]}</center>', False, stack

    else:
        return f'<b>{cleanName.capitalize()} is not an acceptable block.</b>', False, stack
    
    

# Load the .JSON of the project and return the sites HTML to the template
def LoadProject(id):
    # Load HTML for 404 page
    nest_stack = []
    
    _404 = '''
    <link rel="stylesheet" type="text/css" href="/static/BlockWeb.css">
    <div class="Main_text">HTTP: 404 ERROR</div>
    <img src="/static/404Logo.png" alt="404 image" width=360 height=360 class="image">
    <div class="description">It seems there is not a BlockWeb page here</div>
    '''

    # Get the project.json via the projects api.
    project = requests.get(f'https://projects.scratch.mit.edu/{id}')
    if project.status_code == 404:
        return _404 # Return the HTML 404 page if there is no BlockWeb page.

    blocks = project.json()['targets'][0]['blocks'] #Get all the blocks in the project

    #Check to see if the project is shared.
    shared = requests.get(f'https://api.scratch.mit.edu/projects/{id}')
    if shared.status_code == 404:
        return _404 # Return the HTML 404 page if there is no BlockWeb page.

    # Loop through every block in the project
    RAW_HTML = ''
    RAW_CSS = ''

    isFirstEvent = True

    relevant_blocks = {}
    next_block = None
    for key in blocks:
        # If the block is a call of a custom block advance.
        if blocks[key]['opcode'] == 'procedures_call':
            relevant_blocks[key] = {'name': blocks[key]['mutation']['proccode'].split(' %s')[0].lower(), 'inputs': blocks[key]['inputs'], 'next': blocks[key]['next']}
        elif blocks[key]['opcode'] == 'event_whenflagclicked':
            if isFirstEvent:
                next_block = blocks[key]['next']
                not isFirstEvent

    nest_stack = []
    final_block = False
    while not final_block:
        this_block = relevant_blocks[next_block]
        inputArray = []
        for _input in this_block['inputs']:
            inputArray.append(this_block['inputs'][_input][1][1])

        if this_block['name'] in ['div', 'link', 'span', 'p', 'ordered list', 'unordered list', 'list item']:
            nest_stack.append(this_block['name'])

        markup, css, nest_stack = loadBlockMarkup(this_block['name'], inputArray, nest_stack)


        if not str(markup) == 'None':
            if not css:
                RAW_HTML += str(markup)
            else:
                RAW_CSS += str(markup)

            
        
        next_block = this_block['next']
        if next_block == None:
            final_block = True

    output = RAW_HTML + f'<script>document.title="{shared.json()["title"]}";</script><style>{RAW_CSS}</style>'
    print(output)
    return output
    
# Route the project to the correct URL.
@app.route('/projects/<id>/')
def projectPage(id):
    # Parse project.json and return appropriate HTML
    return render_template('site.html', LoadProject=LoadProject, _id=id)
    

# Run the app if the file is being run directly.
if __name__ == '__main__':
    app.run(host='localhost')
