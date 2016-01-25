import ConfigParser
from flask import Flask
import httplib2
import hashlib
from tempfile import NamedTemporaryFile
from os import rename

Config = ConfigParser.ConfigParser()
Config.read('updater.ini')
DEBUG = Config.getboolean('General', 'Debug')
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
    try:
        h = httplib2.Http(".cache")
        h.add_credentials(AuthUsername, AuthPassword)
        resp, content = h.request(UpdateURL,headers={'cache-control':'no-cache'})

        if resp.status == 200:
            if resp['content-type'] == 'text/plain':
                try:
                    with NamedTemporaryFile('w', dir='/tmp', delete=False) as tf:
                        tf.write(content)
                        tempname = tf.name

                    rename(tempname, OutputFile)

                    return 'Success: ' + hashlib.md5(content).hexdigest()
                except:
                    return 'Error: could not write-replace output file'
            else:
                return 'Error: content type not text/plain on response'

        elif resp.status == 401:
            return 'Error: auth failed, check user/password credentials in config'
        elif resp.status == 404:
            return 'Error: URL not found, check update URL in config'
        else:
            return 'Error: received ' + resp['status'] + ' on response'
    except httplib2.ServerNotFoundError as e:
        return 'Error: cannot resolve auth backend server hostname'
    except httplib2.HttpLib2Error as e:
        return 'Error: general error contacting auth backend server'
    except:
        return 'Error: unknown exception'

if __name__ == "__main__":
    app.run(host=FlaskHost, port=FlaskPort)
