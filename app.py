from flask import (
    Flask,
    request,
    render_template,
    session,
)
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError
# from flask import abort, redirect, url_for
# from flaskr import app
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase
import json
import os

with open("./config/firebase.json") as file:
    file_json = json.loads(file.read())
firebase = pyrebase.initialize_app(file_json)
auth = firebase.auth()

app = Flask(__name__)
# for security
app.config['SECRET_KEY'] = os.urandom(256)

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': file_json["projectId"],
})
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./config/flasktest-6898c-e8aeaa7ab788.json"
db = firestore.client()


@app.route("/", methods=['GET'])
@app.route("/index", methods=["GET"])
def index():
    return render_template("index.html")
    # return redirect(url_for("index"))
    # return abort(404)


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        userId = user["localId"]
        session["userId"] = userId
        loginUser = db.collection("users").document(userId).get()
        userInfo = loginUser.to_dict()
        userInfo = sorted(userInfo.items())
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo))
    except:
        return render_template("login.html", msg="メールアドレスまたはパスワードが間違っています。")


@ app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template("regist.html")
    userName = request.form.get("userName")
    email = request.form['email']
    password = request.form['password']
    try:
        user = auth.create_user_with_email_and_password(email, password)
        userId = user["localId"]
        session['userId'] = userId
        loginUser = db.collection("users").document(userId)
        data = {"name": userName}
        loginUser.set(data)
        return render_template("index.html", userInfo=data)
    except:
        return render_template("regist.html", msg="メールアドレスまたはパスワードが登録できないです。")


@app.route("/add", methods=["POST"])
def add():
    try:
        if session.get("userId") is None:
            return render_template("index.html", msg="セッションが切れました。")
        loginUser = db.collection("users").document(session["userId"])
        userInfo = loginUser.get().to_dict()
        field = request.form.get("field")
        value = request.form.get("value")
        userInfo[field] = value
        loginUser.set(userInfo)
        userInfo = sorted(userInfo.items())
        addMsg = field + "ステータスの" + value + "を追加しました。"
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), addMsg=addMsg)
    except:
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), addMsg="追加できませんでした。")


@app.route("/edit", methods=["POST"])
def edit():
    try:
        if session.get("userId") is None:
            return render_template("index.html", msg="セッションが切れました。")
        loginUser = db.collection("users").document(session["userId"])
        userInfo = loginUser.get().to_dict()
        editInfo = request.form.get("editInfo")
        field = request.form.get("field")
        userInfo[field] = editInfo
        loginUser.update(userInfo)
        userInfo = sorted(userInfo.items())
        editMsg = field + "を" + editInfo + "に変更しました。"
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), editMsg=editMsg)
    except:
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), editMsg="編集できませんでした。")


@app.route("/delete", methods=["POST"])
def delete():
    try:
        if session.get("userId") is None:
            return render_template("index.html", msg="セッションが切れました。")
        loginUser = db.collection("users").document(session["userId"])
        field = request.form.get("field")
        data = {field: firestore.DELETE_FIELD}
        loginUser.update(data)
        userInfo = sorted(loginUser.get().to_dict().items())
        deleteMsg = field + "が削除されました。"
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), deleteMsg=deleteMsg)
    except:
        return render_template("profile.html", userInfo=userInfo, userInfo_len=len(userInfo), deleteMsg="削除できませんでした。")


@app.route('/logout')
def logout():
    if session.get("userId") is not None:
        del session['userId']
    return render_template("index.html")


# @app.errorhandler(InternalServerError)
# @app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
def handle_bad_request(e):
    return render_template("error.html"), 404


if __name__ == "__main__":
    app.run(host="localhost", port=8888, debug=True)
