from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",         
    "password": "root",         
    "database": "kanban_db" 
}

def conectar():
    return mysql.connector.connect(**db_config)

def init_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            funcao VARCHAR(100),
            email VARCHAR(100)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(100) NOT NULL,
            descricao TEXT,
            status VARCHAR(20),
            responsavel_id INT,
            FOREIGN KEY (responsavel_id) REFERENCES membros(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM membros")
    membros = cursor.fetchall()

    tarefas_por_status = {}
    for status in ["A Fazer", "Em Andamento", "Concluído"]:
        cursor.execute('''
            SELECT tarefas.id, tarefas.titulo, tarefas.descricao, tarefas.status, membros.nome 
            FROM tarefas LEFT JOIN membros ON tarefas.responsavel_id = membros.id
            WHERE tarefas.status = %s
        ''', (status,))
        tarefas_por_status[status] = cursor.fetchall()

    conn.close()
    return render_template("index.html", tarefas=tarefas_por_status, membros=membros)

@app.route('/tarefa/nova', methods=['GET', 'POST'])
def nova_tarefa():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        status = request.form['status']
        responsavel = request.form.get('responsavel') or None
        cursor.execute('''
            INSERT INTO tarefas (titulo, descricao, status, responsavel_id)
            VALUES (%s, %s, %s, %s)
        ''', (titulo, descricao, status, responsavel))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM membros")
    membros = cursor.fetchall()
    conn.close()
    return render_template('tarefa_form.html', membros=membros)

@app.route('/tarefa/editar/<int:id>', methods=['GET', 'POST'])
def editar_tarefa(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        status = request.form['status']
        responsavel = request.form.get('responsavel') or None
        cursor.execute('''
            UPDATE tarefas SET titulo = %s, descricao = %s, status = %s, responsavel_id = %s
            WHERE id = %s
        ''', (titulo, descricao, status, responsavel, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM tarefas WHERE id = %s", (id,))
    tarefa = cursor.fetchone()
    cursor.execute("SELECT * FROM membros")
    membros = cursor.fetchall()
    conn.close()
    return render_template('editar_tarefa.html', tarefa=tarefa, membros=membros)

@app.route('/tarefa/excluir/<int:id>')
def excluir_tarefa(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/membro/novo', methods=['GET', 'POST'])
def novo_membro():
    if request.method == 'POST':
        nome = request.form['nome']
        funcao = request.form['funcao']
        email = request.form['email']
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO membros (nome, funcao, email) VALUES (%s, %s, %s)", (nome, funcao, email))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('membro_form.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
