import secrets
import bcrypt
import os
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session, abort
import sqlite3


app = Flask(__name__)#, static_url_path='/static')
# Gera uma chave secreta hexadecimal de 16 bytes (32 caracteres)
app.secret_key = secrets.token_hex(16)  


# Cria um cursor
def get_connection():
    return sqlite3.connect('instance/salao_festas.db')
    

'''def get_users_names():
    with get_connection() as conn: 
        cursor = conn.cursor() #usando o cursor em uma mesma thread
        cursor.execute('SELECT nome from usuario')
        # Recupere todos os resultados como uma lista de tuplas
        result = cursor.fetchall()

        names = []

        for r in result:
            name = r[0] #coluna 0 é a coluna nome armazenada no result
            names.append(name)
    
        return names

def get_username_by_id(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM usuario WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None 

def get_categories_infos():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, genero, ano_lancamento, descricao_curta, descricao_completa, url_imagem FROM jogos')
        result = cursor.fetchall()

        infos = []

        for row in result:
            id, nome, genero, ano_lancamento, descricao_curta, descricao_completa, url_imagem = row
            infos.append({'id': id, 'nome': nome, 'genero': genero, 'ano_lancamento': ano_lancamento, 'descricao_curta': descricao_curta, 'descricao_completa': descricao_completa, 'url_imagem': url_imagem})
    return infos'''

def get_clientes():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cliente')
        clientes = cursor.fetchall()

        return clientes
    
'''def get_wishlist_by_user_id(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT jogos.id, jogos.nome, jogos.genero, jogos.ano_lancamento, jogos.descricao_curta, jogos.descricao_completa, jogos.url_imagem FROM lista_de_desejos JOIN jogos ON lista_de_desejos.id_jogo = jogos.id WHERE lista_de_desejos.id_usuario = ?', (user_id,))
        result = cursor.fetchall()

        wishlist = []

        for row in result:
            id, nome, genero, ano_lancamento, descricao_curta, descricao_completa, url_imagem = row
            wishlist.append({'id': id, 'nome': nome, 'genero': genero, 'ano_lancamento': ano_lancamento, 'descricao_curta': descricao_curta, 'descricao_completa': descricao_completa, 'url_imagem': url_imagem})
    
        return wishlist

def get_lista_de_desejos_by_user_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT jogos.*
        FROM lista_de_desejos
        JOIN jogos ON lista_de_desejos.id_jogo = jogos.id
        WHERE lista_de_desejos.id_usuario = ?
    """, (user_id,))
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]
    lista_de_desejos = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return lista_de_desejos
'''
def get_agendamentos_dict():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data, horario, cpf, nome FROM visitacao, cliente WHERE visitacao.cliente_cpf = cliente.cpf')
        todos_agendamentos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return todos_agendamentos

def get_clientes_dict():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cliente')
        clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return clientes    

'''def add_avaliacao(user_id, id_jogo, nota, comentario):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO avaliacao (nota, comentario, id_jogo, id_usuario) VALUES (?, ?, ?, ?)', (nota, comentario, id_jogo, user_id))
        conn.commit()

        recalcula_media_de_notas(id_jogo)

def get_media_de_notas():
    with get_connection() as conn:
        cur = conn.cursor()
        #caso o valor for NULL, substitui por 0
        cur.execute("""
            SELECT id_jogo, COALESCE(AVG(nota), 0.0) as media 
            FROM avaliacao
            GROUP BY id_jogo
        """)
        result = cur.fetchall()

        media_por_jogo = {}

        for row in result:
            id_jogo = row[0]
            media = row[1]

            media_por_jogo[id_jogo] = media

            print(media_por_jogo)  # Debug print

    return media_por_jogo

def update_nota_media():
    media_por_jogo = get_media_de_notas()

    with get_connection() as conn:
        cur = conn.cursor()
        for id_jogo, media in media_por_jogo.items():
            cur.execute("""
                UPDATE jogos
                SET nota_media = ?
                WHERE id = ?
            """, (media, id_jogo))
        conn.commit()


def recalcula_media_de_notas(id_jogo):
    with get_connection() as conn:
        cur = conn.cursor()
        #caso o valor for NULL, substitui por 0
        cur.execute("""
            SELECT COALESCE(AVG(nota), 0.0) as media 
            FROM avaliacao
            WHERE id_jogo = ?
        """, (id_jogo,))
        
        nova_media = cur.fetchone()[0]

        nova_media = round(nova_media, 2) #arredonda para 2 casas decimais

        cur.execute("""
            UPDATE jogos
            SET nota_media = ?
            WHERE id = ?        
        """, (nova_media, id_jogo))
        conn.commit()

def recalcula_media_de_notas_all_games():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM jogos")
        todos_os_ids_de_jogos = cur.fetchall()

        for id_jogo in todos_os_ids_de_jogos:
            recalcula_media_de_notas(id_jogo[0])


def get_ranking():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT jogos.nome, jogos.url_imagem, jogos.descricao_completa, jogos.nota_media, COUNT(avaliacao.id_jogo) as contagem
            FROM jogos
            JOIN avaliacao ON jogos.id = avaliacao.id_jogo
            GROUP BY jogos.id
            ORDER BY nota_media DESC, contagem DESC
        """)
        columns = [column[0] for column in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()] 


 
def create_game(nome_jogo, lancamento_jogo, genero_jogo, descricao_curta, descricao_completa, url_imagem):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO jogos (nome, ano_lancamento, genero, descricao_curta, descricao_completa, url_imagem) VALUES (?, ?, ?, ?, ?, ?)',
                       (nome_jogo, lancamento_jogo, genero_jogo, descricao_curta, descricao_completa, url_imagem))
        conn.commit()


'''

############################################### ROTAS CLIENTE #################################################
# PAGINA INICIAL
@app.route('/home')
@app.route('/')
def home():
    cliente_logado = 'nome_cliente' in session
    nome_cliente = session.get('nome_cliente', '')
    return render_template('html/pages/homepage.html', cliente_logado=cliente_logado, nome_cliente=nome_cliente)

# Página de Produtos
@app.route('/produtos')
def produtos():
    return render_template('html/pages/produtos.html')

# Pagina de serviços
@app.route('/servicos')
def servicos():
    return render_template('html/pages/servicos.html')

# CONTATO
@app.route('/contato')
def contato():
    return render_template('html/pages/contato.html')

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')

        if not cpf or not senha:
            flash('CPF ou senha não fornecidos. Tente novamente!', 'warning')
            return redirect(url_for('login'))

        password_file_path = 'instance/passwords.txt'

        if not os.path.exists(password_file_path):
            flash('Erro ao fazer login. Tente novamente!')
            return redirect(url_for('login'))

        stored_password = None
        with open(password_file_path, 'r') as file:
            for line in file:
                stored_cpf, stored_hashed_password = line.strip().split(',')
                if stored_cpf == cpf:
                    stored_password = stored_hashed_password
                    break

        if stored_password is None or not bcrypt.checkpw(senha.encode('utf-8'), stored_password.encode('utf-8')):
            flash('Cliente não existe ou credenciais incorretas. Tente novamente!')
            return redirect(url_for('login'))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cliente WHERE cpf = ?', (cpf,))
            cliente = cursor.fetchone()

            if cliente is None:
                flash('Usuário não existe ou credenciais incorretas. Tente novamente!')
                return redirect(url_for('login'))
            else:
                session['cpf'] = cliente[0]
                session['nome_cliente'] = cliente[1]
                flash('Login bem sucedido!', 'success')
                if cpf == '000.000.000-00':
                    #session['nome_cliente'] = request.form['nome_cliente']
                    return redirect(url_for('dashboard_admin'))  
                else:
                    #session['nome_cliente'] = request.form['nome_cliente']
                    return redirect(url_for('dashboard_cliente'))  
    return render_template('html/register/login.html')

#LOGOUT
@app.route('/logout')
def logout():
    session.pop('cpf', None)
    session.pop('nome_cliente', None)
    return redirect(url_for('home'))

@app.context_processor
def inject_active():
    def is_active(endpoint): #recebe o endpoint (rota) e verifica se é igual o endpoint atual, se for ele retorna a classeactive, se não retorna vazio
        return 'active' if request.endpoint == endpoint else ''
    return dict(is_active=is_active)

@app.route('/cliente/dashboard-cliente')
@app.route('/admin/dashboard-admin')
def get_events():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nome, data FROM evento')
        eventos = cursor.fetchall()

    eventos_list = [{"title": evento[0], "start": evento[1]} for evento in eventos]

    return render_template('html/pages/cliente/dashboard-cliente.html', eventos=eventos_list)


   # events = [
    #    {"title": "Evento 1", "start": "2023-10-01"},
     #   {"title": "Agendamento 1", "start": "2023-10-02"},
      #  {"title": "Evento 2", "start": "2023-10-03"}
        # Add more events here
    #]
    #return jsonify(events)

#CADASTRAR CLIENTE
@app.route('/cliente/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        celular = request.form['celular']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        confirmarSenha = request.form['confirmar_senha']

        #exceção de formulário incompleto
        if nome == "":
            flash('Preencha o campo Nome!', 'warning')
        elif celular == "":
            flash('Preencha o campo Celular!', 'warning')
        elif cpf == "":
            flash('Preencha o campo CPF!', 'warning')
        elif endereco == "":
            flash('Preencha o campo Endereço!', 'warning')
        elif senha == "":
            flash('Preencha o campo Senha!', 'warning')
        elif confirmarSenha == "":
            flash('Preencha o campo Confirmar Senha!', 'warning')

        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        #exceção de nome inválido
        for c in get_clientes():
            if cpf == c:
                flash('Usuário inválido. Tente novamente!', 'warning') 
                return redirect(url_for('cadastrar'))

        #exceção de senhas incompatíveis
        if senha != confirmarSenha:
            flash('As senhas não coincidem. Tente novamente!')
            return redirect(url_for('cadastrar'))
        
        #Inserindo no bd
        with get_connection() as conn:
            try:
                    cursor = conn.cursor()  
                    cursor.execute('INSERT INTO cliente (cpf, nome, celular, endereco) VALUES (?, ?, ?, ?)', (cpf, nome, celular, endereco))
                    conn.commit() 

                    with open('instance/passwords.txt', 'a') as f:
                        f.write(f"{cpf},{hashed_senha.decode('utf-8')}\n")

                    flash('Cliente cadastrado com sucesso!', 'success')
                    return redirect(url_for('login'))
            except:
                    flash('Erro ao cadastrar cliente. Tente novamente!', 'error')

    return render_template('html/pages/cliente/formulario-cliente.html')

#PERFIL CLIENTE
@app.route('/cliente/perfil', methods=['GET', 'POST'])
@app.route('/admin/perfil', methods=['GET'])
def perfil():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cpf, nome, celular, endereco FROM cliente WHERE cpf = ?', (cpf,))
        cliente = cursor.fetchone()

    if not cliente:
        flash('Cliente não encontrado.', 'danger')
        return redirect(url_for('home'))

    return render_template('html/pages/perfil.html', cliente=cliente)

@app.route('/cliente/dashboard-cliente')
def dashboard_cliente():
    return render_template('html/pages/cliente/dashboard-cliente.html')

#ATUALIZAR CLIENTE
@app.route('/cliente/atualizar', methods=['GET', 'POST'])
def atualizar():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        celular = request.form['celular']
        endereco = request.form['endereco']

        if nome == "":
            flash('Preencha o campo Nome!', 'warning')
        elif celular == "":
            flash('Preencha o campo Celular!', 'warning')
        elif endereco == "":
            flash('Preencha o campo Endereço!', 'warning')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE cliente SET nome = ?, celular = ?, endereco = ? WHERE cpf = ?', (nome, celular, endereco, cpf))
            conn.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('perfil'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cpf, nome, celular, endereco FROM cliente WHERE cpf = ?', (cpf,))
        cliente = cursor.fetchone()

    return render_template('html/pages/cliente/atualizar.html', cliente=cliente)

############################ AGENDAMENTOS CLIENTE ################################

#LISTAR TODOS AGENDAMENTOS DE VISITAÇÃO DO CLIENTE
@app.route('/cliente/agendamentos')
def agendamentos_cliente():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM visitacao WHERE cliente_cpf = ?', (cpf,))
        agendamentos = cursor.fetchall()

    return render_template('html/pages/cliente/agendamentos-cliente.html', agendamentos=agendamentos)

#CRIAR NOVO AGENDAMENTO
@app.route('/cliente/agendamentos/novo', methods=['GET', 'POST'])
def novo_agendamento():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form['data']
        horario = request.form['horario']

        if data == "":
            flash('Preencha o campo Data!', 'warning')
        elif horario == "":
            flash('Preencha o campo Hora!', 'warning')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO visitacao (data, horario, cliente_cpf) VALUES (?, ?, ?)', (data, horario, cpf))
            conn.commit()
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('agendamentos_cliente'))

    return render_template('html/pages/cliente/formulario-agendamento.html')

#DELETAR AGENDAMENTO
@app.route('/cliente/agendamentos/cancelar', methods=['POST'])
def cancelar_agendamento():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    data_agendamento = request.form.get('data')
    hora_agendamento = request.form.get('horario')

    print(f"Received data: {data_agendamento}, hora: {hora_agendamento}")  # Debug statement

    if not data_agendamento or not hora_agendamento:
        flash('Dados inválidos para cancelar o agendamento.', 'danger')
        return redirect(url_for('agendamentos_cliente'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM visitacao WHERE data=? AND horario=?', (data_agendamento, hora_agendamento))
            conn.commit()

            if cursor.rowcount == 0:
                flash('Nenhum agendamento encontrado para deletar.', 'warning')
            else:
                flash('Agendamento deletado com sucesso!', 'success')
    except Exception as e:
        print(f"Error deleting agendamento: {e}")  # Debug statement
        flash('Houve um erro ao deletar o agendamento.', 'danger')

    return redirect(url_for('agendamentos_cliente'))

########################## ROTAS EVENTO ###################################

@app.route('/cliente/eventos', methods=['GET'])
def eventos_cliente():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM evento WHERE cliente_cpf = ?', (cpf,))
        eventos = cursor.fetchall()

    return render_template('html/pages/cliente/eventos-cliente.html', eventos=eventos)
        
################################### ROTAS ADMIN ########################################
@app.route('/dashboard-admin', methods=['GET', 'POST'])
def dashboard_admin():
    return render_template('html/pages/admin/dashboard-admin.html')
    
@app.route('/admin/clientes', methods=['GET'])
def clientes_admin():
    clientes = get_clientes()
    return render_template('html/pages/admin/clientes-admin.html', clientes=clientes)

@app.route('/admin/agendamentos', methods=['GET'])
def agendamentos_admin():
    todos_agendamentos = get_agendamentos_dict()
    print(todos_agendamentos)

    return render_template('html/pages/admin/agendamentos-admin.html', todos_agendamentos=todos_agendamentos)


@app.route('/admin/eventos', methods=['GET'])
def eventos_admin():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM evento JOIN cliente ON evento.cliente_cpf = cliente.cpf')
        eventos = cursor.fetchall()

    return render_template('html/pages/admin/eventos-admin.html', eventos=eventos)

@app.route('/admin/eventos/novo', methods=['GET', 'POST'])
def novo_evento():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form['data_evento']
        horario = request.form['horario_evento']
        nome = request.form['nome_evento']
        tipo = request.form['tipo_evento']
        cliente_cpf = request.form['cliente_evento']

        if nome == "":
            flash('Preencha o campo Nome!', 'warning')
        elif data == "":
            flash('Preencha o campo Data!', 'warning')
        elif horario == "":
            flash('Preencha o campo Horário!', 'warning')
        elif tipo == "":
            flash('Preencha o campo Tipo!', 'warning')
        elif cliente_cpf == "":
            flash('Preencha o campo CPF do cliente!', 'warning')
        else:
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO evento (data, horario, nome, tipo, cliente_cpf) VALUES (?, ?, ?, ?, ?)', (data, horario, nome, tipo, cliente_cpf))
                    conn.commit()
                    flash('Evento criado com sucesso!', 'success')
                    return redirect(url_for('eventos_admin'))
            except Exception as e:
                flash(f'Erro ao criar o evento: {e}', 'danger')

    clientes = get_clientes()
    return render_template('html/pages/admin/formulario-evento.html', clientes=clientes)

@app.route('/admin/eventos/editar/<data>/<horario>', methods=['GET', 'POST'])
def editar_evento(data, horario):
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nova_data = request.form['data_evento']
        novo_horario = request.form['horario_evento']
        nome = request.form['nome_evento']
        tipo = request.form['tipo_evento']
        cliente_cpf = request.form['cliente_evento']

        if nome == "":
            flash('Preencha o campo Nome!', 'warning')
        elif nova_data == "":
            flash('Preencha o campo Data!', 'warning')
        elif novo_horario == "":
            flash('Preencha o campo Horário!', 'warning')
        elif tipo == "":
            flash('Preencha o campo Tipo!', 'warning')
        elif cliente_cpf == "":
            flash('Preencha o campo CPF do cliente!', 'warning')
        else:
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    print(horario)
                    cursor.execute('UPDATE evento SET data = ?, horario = ?, nome = ?, tipo = ?, cliente_cpf = ? WHERE data = ? AND horario = ?', (nova_data, novo_horario, nome, tipo, cliente_cpf, data, horario))
                    conn.commit()
                    flash('Evento atualizado com sucesso!', 'success')
                    return redirect(url_for('eventos_admin'))
            except Exception as e:
                flash(f'Erro ao atualizar o evento: {e}', 'danger')

        return redirect(url_for('eventos_admin'))        
    
    else:
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT evento.data, evento.horario, evento.nome, evento.tipo, cliente.cpf, cliente.nome FROM evento JOIN cliente ON evento.cliente_cpf = cliente.cpf WHERE evento.data = ? AND evento.horario = ?', (data, horario))
                evento = cursor.fetchone()
                clientes = get_clientes()

                if evento:
                    return render_template('html/pages/admin/editar-evento.html', evento=evento, clientes=clientes)
                else:
                    flash('Evento não encontrado.', 'warning')
                    return redirect(url_for('eventos_admin'))
        except Exception as e:
            flash(f'Erro ao carregar o evento: {e}', 'danger')
            return redirect(url_for('eventos_admin'))
        
@app.route('/admin/eventos/deletar/<data>/<horario>', methods=['POST'])
def deletar_evento(data, horario):
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM evento WHERE data = ? AND horario = ?', (data, horario))
            conn.commit()
            flash('Evento deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar o evento: {e}', 'danger')

    return redirect(url_for('eventos_admin'))
                
@app.route('/admin/eventos/cancelar', methods=['POST'])
def cancelar_evento():
    data_evento = request.form.get('data')
    hora_evento = request.form.get('horario')

    if not data_evento or not hora_evento:
        flash('Dados inválidos para cancelar o evento.', 'danger')
        return redirect(url_for('eventos_admin'))
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM evento WHERE data=? AND horario=?', (data_evento, hora_evento))
            conn.commit()

            if cursor.rowcount == 0:
                flash('Nenhum evento encontrado para deletar.', 'warning')
            else:
                flash('Evento cancelado com sucesso!', 'success')
    except Exception as e:
        print(f"Error deleting evento: {e}")
        flash('Houve um erro ao deletar o evento.', 'danger')
    

@app.route('/admin/pagamentos', methods=['GET', 'POST'])
def pagamentos_admin():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pagamento.id_pagto, pagamento.forma_pagto, pagamento.qtd_parcelas, pagamento.evento_data, pagamento.evento_horario, pagamento.valor, pagamento.data_pagto, evento.nome FROM evento JOIN pagamento ON evento_data=data AND evento_horario=horario')
        pagamentos = cursor.fetchall()

    return render_template('html/pages/admin/pagamentos-admin.html', pagamentos=pagamentos)

@app.route('/admin/pagamentos/novo', methods=['GET', 'POST'])
def novo_pagamento():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        forma_pagto = request.form['forma_pagto']
        qtd_parcelas = request.form['qtd_parcelas']
        evento = request.form['evento']
        valor = request.form['valor']
        data = request.form['data']

        try:
            evento_data, evento_horario = evento.split(',')
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO pagamento (forma_pagto, qtd_parcelas, evento_data, evento_horario, valor, data_pagto) VALUES (?, ?, ?, ?, ?, ?)', 
                    (forma_pagto, qtd_parcelas, evento_data, evento_horario, valor, data)
                )
                conn.commit()
                flash('Pagamento criado com sucesso!', 'success')
                return redirect(url_for('pagamentos_admin'))
        except Exception as e:
            flash(f'Erro ao criar o pagamento: {e}', 'danger')
   
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data, horario, nome FROM evento')
        eventos = cursor.fetchall()

    return render_template('html/pages/admin/formulario-pagamento.html', eventos=eventos)

@app.route('/admin/pagamentos/editar/<int:id_pagto>', methods=['GET', 'POST'])
def editar_pagamento(id_pagto):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        forma_pagto = request.form['forma_pagto']
        qtd_parcelas = request.form['qtd_parcelas']
        evento = request.form['evento']
        valor = request.form['valor']
        data = request.form['data']

        try:
            evento_data, evento_horario = evento.split(',')
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE pagamento SET forma_pagto = ?, qtd_parcelas = ?, evento_data = ?, evento_horario = ?, valor = ?, data_pagto = ? WHERE id_pagto = ?', 
                    (forma_pagto, qtd_parcelas, evento_data, evento_horario, valor, data, id_pagto)
                )
                conn.commit()
                flash('Pagamento atualizado com sucesso!', 'success')
                return redirect(url_for('pagamentos_admin'))
        except Exception as e:
            flash(f'Erro ao atualizar o pagamento: {e}', 'danger')
   
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data, horario, nome FROM evento')
        eventos = cursor.fetchall()
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pagamento WHERE id_pagto = ?', (id_pagto,))
        pagamento = cursor.fetchone()
        print(pagamento)

    return render_template('html/pages/admin/editar-pagamento.html',id_pagto=id_pagto, eventos=eventos, pagamento=pagamento)

@app.route('/admin/pagamentos/deletar/<int:id_pagto>', methods=['POST'])
def deletar_pagamento(id_pagto):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM pagamento WHERE id_pagto = ?', (id_pagto,))
            conn.commit()
            flash('Pagamento deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar o pagamento: {e}', 'danger')

    return redirect(url_for('pagamentos_admin'))

@app.route('/admin/parceiros', methods=['GET', 'POST'])
def parceiros_admin():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM parceiro')
        parceiros = cursor.fetchall()

    return render_template('html/pages/admin/parceiros-admin.html', parceiros=parceiros)

@app.route('/admin/parceiros/novo', methods=['GET', 'POST'])
def novo_parceiro():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        celular = request.form['celular']

        # Input validation
        if not nome or not celular:
            flash('Todos os campos são obrigatórios.', 'warning')
            return redirect(url_for('parceiros_admin'))

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO parceiro (nome, celular) VALUES (?, ?)', (nome, celular))
                conn.commit()
                flash('Parceiro criado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao criar o parceiro: {e}', 'danger')

        return redirect(url_for('parceiros_admin'))

    return render_template('html/pages/admin/formulario-parceiro.html')

@app.route('/admin/parceiros/editar/<int:id_parceiro>', methods=['GET', 'POST'])
def editar_parceiro(id_parceiro):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        celular = request.form['celular']

        # Input validation
        if not nome or not celular:
            flash('Todos os campos são obrigatórios.', 'warning')
            return redirect(url_for('parceiros_admin'))

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE parceiro SET nome = ?, celular = ? WHERE id_parceiro = ?', (nome, celular, id_parceiro))
                conn.commit()
                flash('Parceiro atualizado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar o parceiro: {e}', 'danger')

        return redirect(url_for('parceiros_admin'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM parceiro WHERE id_parceiro = ?', (id_parceiro,))
        parceiro = cursor.fetchone()

    return render_template('html/pages/admin/editar-parceiro.html', id_parceiro=id_parceiro, parceiro=parceiro)

@app.route('/admin/parceiros/deletar/<int:id_parceiro>', methods=['POST'])
def deletar_parceiro(id_parceiro):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM parceiro WHERE id_parceiro = ?', (id_parceiro,))
            conn.commit()
            flash('Parceiro deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar o parceiro: {e}', 'danger')

    return redirect(url_for('parceiros_admin'))


#@app.route('/categories')
#def categories():
#    games = get_games()
#    return render_template('html/pages/categories.html', games=games)


#@app.route('/ranking')
##def ranking():
#    ranking = get_ranking()
#    return render_template('html/pages/ranking.html', ranking=ranking)

##@app.route('/perfil', methods=['GET', 'POST'])
#def profile():
 #   if 'id_usuario' in session:
  #      id_usuario = session['id_usuario']
   #     usuario_nome = get_username_by_id(id_usuario)
    #    #lista_de_desejos = get_lista_de_desejos_by_user_id(user_id)
    #    agendamentos = get_agendamentos_dict()  # Buscar todos os agendamentos do cliente
    #    if agendamentos is None:
     #       agendamentos = []
        #if request.method == 'POST':
            #id_agendamento = request.form.get('agendamento')
            #nota = request.form.get('nota')
            #comentario = request.form.get('comentario')
            #add_avaliacao(user_id, id_jogo, nota, comentario)
            #flash('Avaliação enviada com sucesso!', 'success')
      #      return redirect(url_for('profile'))  # Redireciona para a mesma página
       # return render_template('html/pages/profile.html', nome=usuario_nome, agendamentos=agendammentos)
    #else:
    #    flash('Você precisa fazer login para acessar esta página.', 'warning')
     ##   return redirect(url_for('login'))

#@app.route('/adminpage', methods=['GET', 'POST'])
#def adminpage():
#    if request.method == 'POST':
#        nome = request.form['nome']
#        lancamento = request.form['lancamento']
#        genero = request.form['genero']
#        descricao_curta = request.form['descricao_curta']
#        descricao_completa = request.form['descricao_completa']
#        url_imagem = request.form['url_imagem']
#
 #       if nome == "":
  #          flash('Preencha o campo Nome!', 'warning')
   #     elif lancamento == "":
    #        flash('Preencha o campo Ano de lançamento!', 'warning')
     #   elif genero == "":
      #      flash('Preencha o campo Gênero!', 'warning')
       # elif descricao_curta == "":
        #    flash('Preencha o campo Descrição curta!', 'warning')
        #elif descricao_completa == "":
        #    flash('Preencha o campo de Descrição completa!', 'warning')
        #elif url_imagem == "":
        #    flash('Preencha o campo de URL da imagem!', 'warning')

        #create_game(nome, lancamento, genero, descricao_curta, descricao_completa, url_imagem)
        #flash(f'Jogo "{nome}" adicionado com sucesso!', 'success')

    #games = get_games_dict()
    #return render_template('html/pages/adminpage.html', games=games)

#@app.route('/add_to_wishlist', methods=['POST'])
#def add_to_wishlist():
#    if 'user_id' not in session:
#        abort(403)  # Retorna um erro 403 se o usuário não estiver logado

#    game_id = request.form.get('game_id')
#    user_id = session['user_id']

#    with get_connection() as conn:
#        cursor = conn.cursor()
#        cursor.execute('INSERT INTO lista_de_desejos (id_jogo, id_usuario) VALUES (?, ?)', (game_id, user_id))
#        conn.commit()

 #   return '', 204  # Retorna um status 204 (No Content) para indicar que a operação foi bem-sucedida

#@app.route('/delete_game', methods=['DELETE'])
#def delete_game():
#    id_jogo = request.form.get('game_id')

   # with get_connection() as conn:   
   #     cursor = conn.cursor()
   #     cursor.execute('DELETE FROM jogos WHERE id = ?', (id_jogo,))
   #     conn.commit()
    
   # return '', 204  # Retorna um status 204 (No Content) para indicar que a operação foi bem-sucedida

#@app.route('/update_game', methods=['PUT'])
#def update_game():  
#    id_jogo = request.form.get('game_id')
#    nome_jogo = request.form.get('nome')
#    lancamento_jogo = request.form.get('lancamento')
#    genero_jogo = request.form.get('genero')
#    descricao_curta = request.form.get('descricao_curta')
#    descricao_completa = request.form.get('descricao_completa')
#    url_imagem = request.form.get('url')

 #   with get_connection() as conn:
  #      cursor = conn.cursor()
   #     cursor.execute('UPDATE jogos SET nome = ?, ano_lancamento = ?, genero = ?, descricao_curta = ?, descricao_completa = ?, url_imagem = ? WHERE id = ?', 
    #                   (nome_jogo, lancamento_jogo, genero_jogo, descricao_curta, descricao_completa, url_imagem, id_jogo))
    #    conn.commit()
    
   # return '', 204

if __name__ == '__main__':
    #recalcula_media_de_notas_all_games()
    app.run(debug=True)