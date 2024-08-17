import base64
import csv
import datetime
import json
import time
from PIL import Image
from flask import Flask, jsonify, render_template, request, redirect, make_response
from sqlalchemy import update
from flask_login import login_required, logout_user
from yandexGPTtest import StreamResponse

from forms.login import *
from forms.register import *

from data.user import Users
from data.context import ChatHistory


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-arrow-project'
app.static_folder = 'static'

login_manager = LoginManager()
login_manager.init_app(app)


file_path_token = 'tokens.csv' 
with open(file_path_token, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    lstdata = list(reader)
    catalog_text_art, identifier, apikey_text_art = lstdata[0]['catalog'], lstdata[0]['identifier'], lstdata[0]['apikey']
    catalog_syn, identifier, apikey_syn = lstdata[1]['catalog'], lstdata[1]['identifier'], lstdata[1]['apikey']


db_session.global_init("db/history.db")

@login_required
@app.route('/')
def hello():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    db_sess = db_session.create_session()
    return render_template('main.html', current_user=current_user)


@login_required
@app.route('/get-message', methods=['POST', 'GET'])
def get_message():
    if request.method == 'POST':
        data = request.get_json()
        user_input = data['message']
        db_sess = db_session.create_session()
        stream = StreamResponse(catalog_text_art, identifier, apikey_text_art)
        history = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
        history_lst = []
        for i in history:
            if i.is_user:
                history_lst.append({'author': 'user', 'text': i.context})
            else:
                history_lst.append({'author': 'bot', 'text': i.context})
        history_lst.append({'author': 'user', 'text': user_input})

        response_text = json.loads(stream.GPT_text_response(history_lst))
        LLM_answer = response_text["result"]["alternatives"][0]["message"]["text"]

        db_sess = db_session.create_session()
        user_history = ChatHistory(user_id=current_user.id, is_user=True, context=user_input, is_text=True)
        db_sess.add(user_history)

        assistant_history = ChatHistory(user_id=current_user.id, is_user=False, context=LLM_answer, is_text=True)
        db_sess.add(assistant_history)
        db_sess.commit()
        return jsonify({'message': LLM_answer})
    

@login_required
@app.route('/get-art', methods=['GET', 'POST'])
def get_art():
    stream = StreamResponse(catalog_text_art, identifier, apikey_text_art)
    db_sess = db_session.create_session()
    last_message = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id and ChatHistory.is_text == True).order_by(ChatHistory.id).all()[-1].context
    count = len(last_message)
    if count > 500:
        return jsonify({'image': False})
    response_id = stream.GPT_ART_response(last_message)
    if response_id == False:
        return jsonify({'image': False})
    resp = make_response('response_id')
    resp.set_cookie('response_id', response_id, max_age=70)
    return resp


@login_required
@app.route('/get-art-ready', methods=["POST", "GET"])
def get_art_ready():
    db_sess = db_session.create_session()
    data = request.get_json()
    response_id = data['message']
    stream = StreamResponse(catalog_text_art, identifier, apikey_text_art)
    image_bytes = stream.GPT_ART_ready_response(response_id)
    if image_bytes != False:
        with open(f'static/images/{response_id}.jpeg', 'wb') as f:
            f.write(image_bytes)
        db_sess.add(ChatHistory(user_id=current_user.id, is_user=False, context=f'static/images/{response_id}.jpeg', is_text=False))
        db_sess.commit()
        path = f'static/images/{response_id}.jpeg'
        img = Image.open(path)
        img = img.resize((400, 400))
        img.save(path)
        return jsonify({'image': path})
    else:
        return jsonify({'image': False})
    

@login_required
@app.route('/speech-synthesis', methods=['POST', 'GET'])
def speech_synthesis(): 
    db_sess = db_session.create_session()
    text = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id, ChatHistory.is_text == True).order_by(ChatHistory.id).all()[-1].context
    stream = StreamResponse(catalog_syn, identifier, apikey_syn)
    response = stream.speech_synthesis(text)
    path = f'static/audio/{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.ogg'
    response.export(path, "wav")
    db_sess.add(ChatHistory(user_id=current_user.id, is_user=False, context=path, is_text=False))
    db_sess.commit()
    return jsonify({'audio': path})

@app.route('/art-is-not-ready')
def art_is_not_ready():
    return render_template('art-is-not-ready.html')


@login_required
@app.route('/get-history')
def get_history():
    db_sess = db_session.create_session()
    history = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
    history_lst = []
    for i in history:
        if i.is_user:
            history_lst.append({'author': 'user', 'text': i.context})
        else:
            if '.jpeg' in i.context:
                history_lst.append({'author': 'bot-art', 'text': i.context})
            elif '.ogg' in i.context:
                history_lst.append({'author': 'bot-audio', 'text': i.context})
            else:
                history_lst.append({'author': 'bot', 'text': i.context})
    return jsonify(history_lst)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
            message="Неправильный логин или пароль",
            form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                form=form,
                message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Users).filter(Users.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                form=form,
                message="Такой пользователь уже есть")
        user = Users(login=form.login.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(401)
def unauthorized(error):
    return render_template('unauthorized.html')


if __name__ == '__main__':
    app.run()
