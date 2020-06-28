from flask import Flask
from flask import request, jsonify, render_template
from flask_cors import CORS
from src.dao import create
from src.server.readapis.authread import authread
from src.server.util import SUCCESS_RESULT

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder="../../assets/static",
    template_folder="../../assets/template"
)
app.register_blueprint(authread, url_prefix="/auth")
CORS(app)

@app.route("/")
def check():
    return jsonify(SUCCESS_RESULT)


@app.route("/ui")
def render():
    return render_template("main.html")


# Main func
def run_server():
    app.run(debug=True, host="0.0.0.0")
