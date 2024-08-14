import csv
import json
from flask import Flask, jsonify, render_template, request, redirect
from sqlalchemy import update
from flask_login import login_required, logout_user
from yandexGPTtest import StreamResponse

from forms.login import *
from forms.register import *

from data.user import Users
from data.context import ChatHistory


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-arrow-project'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("ai-arrow-project/db/history.db")

@login_required
@app.route('/')
def hello():
    db_sess = db_session.create_session()
    return render_template('main.html', current_user=current_user)

@login_required
@app.route('/get-message', methods=['POST'])
def get_message():
    if request.method == 'POST':
        data = request.get_json()
        # print(data)

        user_input = data['message']

        db_sess = db_session.create_session()

        file_path_token = 'ai-arrow-project/tokens.csv' 
        with open(file_path_token, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            catalog, identifier, apikey = None, None, None
            for row in reader:
                catalog = row['catalog']
                identifier = row['identifier']
                apikey = row['apikey']
        stream = StreamResponse(catalog, identifier, apikey)
        history = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
        history_lst = []
        for i in history:
            if i.is_user:
                history_lst.append({'author': 'user', 'text': i.context})
            else:
                history_lst.append({'author': 'bot', 'text': i.context})
        history_lst.append({'author': 'user', 'text': user_input})
        
        response_text = json.loads(stream.response(history_lst))
        LLM_answer = response_text["result"]["alternatives"][0]["message"]["text"]

        db_sess = db_session.create_session()
        user_history = ChatHistory(user_id=current_user.id, is_user=True, context=user_input)
        db_sess.add(user_history)

        assistant_history = ChatHistory(user_id=current_user.id, is_user=False, context=LLM_answer)
        db_sess.add(assistant_history)
        db_sess.commit()
        return jsonify({'message': LLM_answer})
    

@app.route('/get-history')
def get_history():
    db_sess = db_session.create_session()
    history = db_sess.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).all()
    history_lst = []
    for i in history:
        if i.is_user:
            history_lst.append({'author': 'user', 'text': i.context})
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
    app.run(debug=True)
