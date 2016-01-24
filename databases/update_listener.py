from flask import Flask
import httplib2
import hashlib

app = Flask(__name__)

@app.route('/')
def hello():
    return ""

@app.route('/refresh')
def refresh():
    h = httplib2.Http(".cache")
    #h.add_credentials('name', 'password')
    resp, content = h.request("http://192.168.0.1/",
                              headers={'cache-control':'no-cache'})

    print resp
    
    if resp['status'] == '200' and resp['content-type'] == 'text/html':
        try:
            with open('update.acl', 'w') as f:
                f.write(content)
            
            return 'Success ' + hashlib.md5(content).hexdigest()
        except:
            return 'Error could not write output file'
        
    else:
        return 'Error ' + resp['status']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
