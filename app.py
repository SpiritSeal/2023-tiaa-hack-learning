from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import openai
import hashlib
import sys

app = Flask(__name__)

BUF_SIZE = 65536

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'uploads'

OPENAI_APIKEY = None

with open('openaiapi.key', 'r') as f:
    OPENAI_APIKEY = f.read()
OPENAI_APIKEY = OPENAI_APIKEY.strip()

assert OPENAI_APIKEY is not None
openai.api_key = OPENAI_APIKEY

# home page


@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_hash(file):
    md5 = hashlib.md5()
    print(file)
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return "MD5: {0}".format(md5.hexdigest())


@app.route("/goodnight/<file>")
def parse_file(file):

    file = f'uploads/{file}'
    file_hash = get_file_hash(file)
    rf = read_file(file)
    title_prompt = f"Provide me the title to this information {rf}"
    openai.Model.list()
    title_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible."},
                  {"role": "user", "content": "How are you?"},
                  {"role": "assistant", "content": "I am doing well"},
                  {"role": "user", "content": title_prompt}]
    )
    summary_prompt = f"Provide me a summary of this information {rf}"
    summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible."},
                  {"role": "user", "content": "How are you?"},
                  {"role": "assistant", "content": "I am doing well"},
                  {"role": "user", "content": summary_prompt}]
    )

    print(summary_response)

    return render_template("index2.html", title="Goodnight", title_resp=title_response, sum_resp=summary_response['choices'[1]][1], hash=file_hash)


@ app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(f'goodnight/{filename}')
    return render_template('uploadPage.html')


def read_file(file):
    f = open(file, "r", encoding="utf-8")
    return f.read()
