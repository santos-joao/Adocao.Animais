import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from utilidades import *

app = Flask(__name__)
app.secret_key = 'chave_flask_super_secreta'

db_config = {
    'user': 'python',
    'password': 'Aula@123',
    'host': 'adocaonimais.mysql.database.azure.com',
    'port': '3306' ,
    'database': 'adocaoanimais'
}

@app.route('/')
def index():
    is_logged_in = 'usuario_logado' in session
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome').title()
        sobrenome = request.form.get('sobrenome').title()
        email = request.form.get('email')
        senha = request.form.get('senha')

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
            query = "SELECT senha FROM login WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('login.html', erro="Erro ao realizar o login.")

        if result:
            hashed_senha = result[0]

            if isinstance(hashed_senha, str):
                hashed_senha = hashed_senha.encode('utf-8')

            if verify_senha(senha, hashed_senha):
                session['usuario_logado'] = email
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

# Rota para fazer logout do sistema
@app.route('/logout')
def logout():
    # Remove o usuário logado da sessão
    session.pop('usuario_logado', None)
    # Redireciona para a página inicial (index)
    return redirect(url_for('index'))

@app.route('/adotar')
def adotar():
    return render_template('adotar.html')

@app.route('/blog')
def blog():
    # Redireciona para a página inicial (index)
    return render_template('blog.html')

@app.route('/config')
def config():
    return render_template('config.html')

if __name__ == '__main__':
    app.run(debug=True)


# > cadastro
# - email
#   - email só é válido se tiver @ e se terminar com .com ou .com.br

# > index
# - mudar card ao lado do mapa