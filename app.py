from flask import Flask,render_template, request
import requests
import json

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
base_url = app.config["FMEURL"]
repo = app.config["FMEREPO"]
workspace = app.config["FMEWORKSPACE"]

def getToken(usr,pwd):
    """Function to retrieve token from FME server."""
    url = "{}/fmetoken/generate.json?user={}&password={}&update=true".format(base_url, usr, pwd)
    r = requests.get(url)
    response = json.loads(r.text)['serviceResponse']
    token = response['token']
    expiration = response['expirationDate']
    return token,expiration

def runWorkspace(token,repo,workspace):
    """Function to run workspace on FME server."""
    print(token, repo, workspace)
    #url = "{}/fmetoken/generate.json?user={}&password={}&update=true".format(base_url, usr, pwd)
    #r = requests.get(url)
    #return json.loads(r.text)

@app.route('/', methods = ['GET'])
def main():
    """Home page, renders the site's html page."""
    return render_template('site.html')

@app.route('/callFME', methods = ['POST'])
def callFME():
    """When the frontend posts to this address, a token is retrieved,
    followed by a trigger to the export workspace on FME server."""
    token,expiration = getToken(request.form['usr'],request.form['pwd'])
    runWorkspace(token,repo,workspace)
    return json.dumps({"message":"fantastic"})

if __name__ == '__main__':
  	app.run(debug=True)
