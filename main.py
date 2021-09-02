from flask import Flask, render_template
import requests, sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homePage.html')

def loadBlockMarkup(blockname, blockInputs):
    print(blockname, file=sys.stdout)
    if blockname == 'set icon':
        return f'<script>changeFavicon({blockInputs[0]});<script>\n'

def LoadProject(id):
    blocks = requests.get(f'https://projects.scratch.mit.edu/{id}').json()['targets'][0]['blocks']
    if requests.get(f'https://api.scratch.mit.edu/projects/{id}').status_code == 404:
        return 'It appears there is not a scratchweb project here' # Return the HTML 404 page if there is no ScratchWeb page.

    RAW_HTML = 'Hello'
    for key in blocks:
        if blocks[key]['opcode'] == 'procedures_call':
            inputs = blocks[key]['inputs']
            
            blockName = blocks[key]['mutation']['proccode'].split(' %s')[0].lower()

            input_array = []
            for _input in inputs:
                input_array.append(inputs[_input][1][1])

            RAW_HTML += str(loadBlockMarkup(blockName, input_array))

    return RAW_HTML
    

@app.route('/projects/<id>/')
def projectPage(id):
    # Parse project.json and return appropriate HTML
    print(id)
    return render_template('site.html', LoadProject=LoadProject, _id=id)
    


if __name__ == '__main__':
    app.run(host='localhost')