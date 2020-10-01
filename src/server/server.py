from flask import Flask
from flask import request, jsonify, render_template
from flask_cors import CORS
from src.dao import create
from src.server.readapis.authread import authread
from src.server.readapis.gameread import gameread
from src.server.readapis.imgread import imgread
from src.server.writeapis.authmod import authmod
from src.server.util import SUCCESS_RESULT

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder="../../assets/static",
    template_folder="../../assets/template"
)
app.register_blueprint(authread, url_prefix="/read")
app.register_blueprint(gameread, url_prefix="/search")
app.register_blueprint(authmod, url_prefix="/write")
app.register_blueprint(imgread, url_prefix="/getimg")
CORS(app)

@app.route("/")
def check():
    return jsonify(SUCCESS_RESULT)


@app.route("/ui")
def render():
    return render_template("main.html")


@app.route("/uis")
def render_selects():
    return render_template("select.html")


# Main func
def run_server():
    app.run(debug=True, host="0.0.0.0", port=5001)
