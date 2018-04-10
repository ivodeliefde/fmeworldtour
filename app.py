################################################################################
# Import dependencies

from flask import Flask,render_template, request, send_file
from copy import deepcopy
from bs4 import BeautifulSoup
import urllib
import requests
import zipfile
import json
import uuid
import os

################################################################################
# Setup app and config

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
base_url = app.config["FMEURL"]
repo = app.config["FMEREPO"]
workspace = app.config["FMEWORKSPACE"]
temp_path = os.path.join(os.getcwd(), app.config["TEMP"])

################################################################################
# Helper functions

# -- FME stuff --
def getToken(usr,pwd):
    """Function to retrieve token from FME server."""
    url = "{}/fmetoken/generate.json?user={}&password={}&update=true".format(base_url, usr, pwd)
    r = requests.get(url)
    response = json.loads(r.text)['serviceResponse']
    token = response['token']
    expiration = response['expirationDate']
    return token,expiration

def runDownloadService(repo,workspace,token,params):
    """Function to run workspace on FME server."""
    print(repo,workspace,token)
    url = "{}/fmedatadownload/{}/{}?{}&token={}".format(base_url,repo,workspace,params,token)
    print(url)
    r = requests.get(url)
    print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    downloadUrl = soup.a.get('href')
    print(downloadUrl)
    return downloadUrl
# -- FME stuff --

# -- File handling --
def downloadFile(url, path):
    """Function to download a file from a URL"""
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)

def unzipFile(file, unzippath):
    """Function to unzip a zipfile to a specific output path"""
    print(file)
    zip_ref = zipfile.ZipFile(file, 'r')
    zip_ref.extractall(unzippath)
    zip_ref.close()

def listAllFiles(path):
    """Function to list all files in a directory"""
    outputFiles = []
    for root, dirs, files in os.walk(path):
        for name in files:
            outputFiles.append(os.path.join(root,name))
    return outputFiles

def prepFiles(url, temp_path):
    """Function to go from an FME download url to files that are ready to be
    downloaded by the user interface"""
    sessionID = str(uuid.uuid4())
    path = os.path.join(temp_path,sessionID)
    os.mkdir(path)
    downloadpath = os.path.join(path, "files.zip")
    extractpath = os.path.join(path, "extracted")
    downloadFile(url, downloadpath)
    os.mkdir(extractpath)
    unzipFile(downloadpath, extractpath)
    files = listAllFiles(extractpath)
    response = {}
    for each in files:
        name = "{}_{}".format(sessionID,os.path.basename(each))
        ext = name.split(".")[-1]
        response[ext] = name
    return response
# -- File handling --

# -- GeoJSON stuff --
def flipCoords(geojson):
    """Function to flip the coordinates of a polygon GeoJSON object"""
    obj = json.loads(geojson)
    for i,ring in enumerate(obj['geometry']['coordinates']):
        for j,coord in enumerate(ring):
            x = coord[0]
            y = coord[1]
            obj['geometry']['coordinates'][i][j] = [y,x]
    return json.dumps(obj)

def reverseOrderCoords(geojson):
    """Function to reverse the order of the coordinates of a polygon GeoJSON
    object (left-hand rule to right-hand rule or vice versa)."""
    obj = json.loads(geojson)
    objReversed = deepcopy(obj)
    objReversed['geometry']['coordinates'] = []
    for i,ring in enumerate(obj['geometry']['coordinates']):
        objReversed['geometry']['coordinates'].append([])
        for j,coord in enumerate(ring):
            # Add coordinates from right to left by applying a -1 multiplier to j
            objReversed['geometry']['coordinates'][i].insert(j*-1, coord)
    return json.dumps(objReversed)
# -- GeoJSON stuff --

################################################################################
# App routing

@app.route('/', methods = ['GET'])
def main():
    """Home page, renders the site's html page."""
    return render_template('site.html')

@app.route('/callFME', methods = ['POST'])
def callFME():
    """When the frontend posts to this address, a token is retrieved,
    followed by a trigger to the export workspace on FME server."""
    token,expiration = getToken(request.form['usr'],request.form['pwd'])
    aoi = reverseOrderCoords(request.form['aoi'])
    params = urllib.parse.quote("&GeoJSON='{}'dataset=NWB&opt_showresult=false&opt_servicemode=sync".format(aoi), safe='')
    downloadUrl = runDownloadService(repo,workspace,token,params)
    response = prepFiles(downloadUrl, temp_path)
    return json.dumps(response)

@app.route("/download/<file_name>", methods=['GET', 'POST'])
def getFile(file_name):
    """When the frontend requests a filename it will be returned as a download"""
    sessionID,name = file_name.split("_")
    filepaths = listAllFiles(os.path.join(temp_path,sessionID))
    for filepath in filepaths:
        if name in filepath:
            return send_file(filepath, as_attachment=True)

################################################################################

if __name__ == '__main__':
    app.run(debug=True)
