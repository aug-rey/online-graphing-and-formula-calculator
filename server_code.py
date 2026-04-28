# here is the backend code used by the server

from flask import Flask, request
from json import dump

app = Flask(__name__)

@app.route("/calculator", methods=["GET"])
def calculator_get():
    with open("/var/www/api/formulas.json", "r") as f:
        return f.read(), 200, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}


@app.route("/calculator", methods=["POST"])
def calculator_post():
    if request.headers["password"] != "": # api secret redacted
        return "Unauthorized", 401, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}
    with open("/var/www/api/formulas.json", "w") as f:
        dump(request.json, f)
    return "Success", 200, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5647, debug=False)
