import mysql.connector
import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from utilidades import *

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.permanent_session_lifetime = timedelta(minutes=30)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

db_config = {
    'user': 'python',
    'password': 'Aula@123',
    'host': 'adocaoanimais.mysql.database.azure.com',
    'port': '3306',
    'database': 'adocaoanimais',
}

@app.route('/')
def index():
    is_logged_in = 'idlogin' in session
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome').title()
        sobrenome = request.form.get('sobrenome').title()
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not (email.endswith('.com') or email.endswith('.com.br')):
            return render_template('cadastro.html', error="Insira um e-mail válido.")

        hashed_senha = hash_senha(senha)

        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "INSERT INTO login (nome, sobrenome, email, senha) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome, sobrenome, email, hashed_senha))
            cnx.commit()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('cadastro.html', erro="Erro ao realizar o cadastro.")

        return redirect(url_for('login'))
    else:
        return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "SELECT idlogin, senha FROM login WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('login.html', erro="Erro ao realizar o login.")

        if result:
            idlogin, hashed_senha = result

            if isinstance(hashed_senha, str):
                hashed_senha = hashed_senha.encode('utf-8')

            if verify_senha(senha, hashed_senha):
                session['idlogin'] = idlogin
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="E-mail ou senha incorretos.")
            
        else:
            return render_template('login.html', error="E-mail ou senha incorretos.")
        
    return render_template('login.html')
    
@app.route('/mudar_senha', methods=['GET', 'POST'])
def mudar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            return render_template('mudar_senha.html', message="As senhas não coincidem.", message_type="danger")

        hashed_nova_senha = hash_senha(nova_senha)

        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "SELECT * FROM login WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if not result:
                return render_template('mudar_senha.html', message="E-mail não encontrado.", message_type="danger")

            update_query = "UPDATE login SET senha = %s WHERE email = %s"
            cursor.execute(update_query, (hashed_nova_senha, email))
            cnx.commit()
            cursor.close()
            cnx.close()

        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('mudar_senha.html', message="Erro ao atualizar a senha.", message_type="danger")

        return render_template('mudar_senha.html', message="Senha atualizada com sucesso!", message_type="success")

    return render_template('mudar_senha.html')

@app.route('/logout')
def logout():
    session.pop('idlogin', None)
    return redirect(url_for('index'))

@app.route('/adotar')
def adotar():
    is_logged_in = 'idlogin' in session
    return render_template('adotar.html', is_logged_in=is_logged_in)

@app.route('/blog')
def blog():
    is_logged_in = 'idlogin' in session
    return render_template('blog.html', is_logged_in=is_logged_in)

@app.route('/config')
def config():
    return render_template('config.html')

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')
