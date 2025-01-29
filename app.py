import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'chave_flask_super_secreta'  # Necessário para usar session

db_config = {
    'user': 'python',
    'password': 'Aula@123',
    'host': 'adocaonimais.mysql.database.azure.com',
    'port': '3306' ,
    'database': 'adocaoanimais'
}
#senha banco: Aula@123

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

        # Inserir no banco
        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "INSERT INTO login (nome, sobrenome, email, senha) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome, sobrenome, email, senha))
            cnx.commit()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('cadastro.html', erro="Erro ao realizar o cadastro.")

        # Após cadastrar, redireciona para página inicial ou outra
        return redirect(url_for('login'))
    else:
        return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Verificar no banco
        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "SELECT COUNT(*) FROM login WHERE email=%s AND senha=%s"
            cursor.execute(query, (email, senha))
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('login.html', erro="Erro ao realizar o login.")

        if result and result[0] == 1:
            # Login OK -> guarda na sessão
            session['usuario_logado'] = email
            return redirect(url_for('index'))
        else:
            # Falha no login -> renderiza login novamente com mensagem de erro
            return render_template('login.html', erro="Usuário ou senha incorretos")
    else:
        return render_template('login.html')

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