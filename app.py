import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'chave_flask_super_secreta'  # Necessário para usar session

db_config = {
    'user': 'adocaonimais.mysql.database.azure.com',
    'password': 'Aula@123',
    'host': 'adocaonimais.mysql.database.azure.com',
    'port': '3306' ,
    'database': 'adocaonimais '
}
#senha banco: Aula@123
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Inserir no banco
        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "INSERT INTO usuario_secretaria (usuario, senha) VALUES (%s, %s)"
            cursor.execute(query, (usuario, senha))
            cnx.commit()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('cadastro.html', erro="Erro ao realizar o cadastro.")

        # Após cadastrar, redireciona para página inicial ou outra
        return redirect(url_for('index'))
    else:
        return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Verificar no banco
        try:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "SELECT COUNT(*) FROM usuario_secretaria WHERE usuario=%s AND senha=%s"
            cursor.execute(query, (usuario, senha))
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar com o banco de dados: {err}")
            return render_template('login.html', erro="Erro ao realizar o login.")

        if result and result[0] == 1:
            # Login OK -> guarda na sessão
            session['usuario_logado'] = usuario
            return redirect(url_for('home'))       
        else:
            # Falha no login -> renderiza login novamente com mensagem de erro
            return render_template('login.html', erro="Usuário ou senha incorretos")
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    if 'usuario_logado' in session:
        return f"Bem-vindo, {session['usuario_logado']}!"
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

# Rota para a página inicial do sistema
@app.route('/home')
def home():
    # Verifica se o usuário está logado na sessão
    if 'usuario_logado' not in session:
        # Redireciona para a página de login se o usuário não estiver logado
        return redirect(url_for('login'))
    # Recupera o nome do usuário logado da sessão
    usuario = session['usuario_logado']
    # Renderiza o template 'home.html', passando o nome do usuário como variável
    return render_template('home.html', usuario=usuario)

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


@app.route('/parceiros')
def parceiros():
    # Redireciona para a página inicial (index)
    return render_template('parceiros.html')
