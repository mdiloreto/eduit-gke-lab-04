
from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    image_name = os.environ.get('IMAGE_NAME', 'No establecido')
    tag_name = os.environ.get('TAG_NAME', 'No establecido')
    pod_name = os.environ.get('POD_NAME', 'No establecido')
    version = "v1.0.0"
    return render_template('index.html', image_name=image_name, tag_name=tag_name, pod_name=pod_name, version=version)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
