import ConfigParser
from flask import Flask
import httplib2
import hashlib

Config = ConfigParser.ConfigParser()
Config.read('updater.ini')
DEBUG = Config.getbool('General', 'Debug')
OutputFile = Config.get('General', 'OutputFile')
FlaskHost = Config.get('Flask', 'Host')
FlaskPort = Config.getint('Flask', 'Port')
AuthUsername = Config.get('AuthBackend', 'AuthUsername')
AuthPassword = Config.get('AuthBackend', 'AuthPassword')
UpdateURL = Config.get('AuthBackend', 'UpdateURL')

app = Flask(__name__)

@app.route('/')
def hello():
    return ""

@app.route('/refresh')
def refresh():
    h = httplib2.Http(".cache")
    h.add_credentials(AuthUsername, AuthPassword)
    resp, content = h.request(UpdateURL,
                              headers={'cache-control':'no-cache'})

    if DEBUG:
        print resp
    
    if resp['status'] == '200':
        if resp['content-type'] == 'text/plain':
            try:
                with open(OutputFile, 'w') as f:
                    f.write(content)
            
                    return 'Success: ' + hashlib.md5(content).hexdigest()
            except:
                return 'Error: could not write output file'
        else:
            return 'Error: content type not text/plain on response'
    else:
        return 'Error: received ' + resp['status'] + ' on response'


if __name__ == "__main__":
    app.run(host=FlaskHost, port=FlaskPort)
