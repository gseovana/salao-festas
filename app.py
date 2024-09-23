from datetime import datetime
from decimal import Decimal
import io
import secrets
import bcrypt
import os
from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session
import sqlite3
from sqlite3 import IntegrityError
from matplotlib.ticker import MaxNLocator
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import matplotlib.pyplot as plt


app = Flask(__name__)#, static_url_path='/static')
# Gera uma chave secreta hexadecimal de 16 bytes (32 caracteres)
app.secret_key = secrets.token_hex(16)  


# Cria um cursor
def get_connection():
    return sqlite3.connect('instance/salao_festas.db')

def get_clientes():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cliente')
        clientes = cursor.fetchall()

        return clientes

def get_mobilias():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mobilia')
        mobilias = cursor.fetchall()

        return mobilias
    
def get_agendamentos_dict():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data, horario, cpf, nome_cliente FROM visitacao, cliente WHERE visitacao.cliente_cpf = cliente.cpf')
        todos_agendamentos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return todos_agendamentos

def get_clientes_dict():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cliente')
        clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return clientes    
    
def format_datetime(value, format='%d/%m/%Y'):
    if value is None:
        return ""
    # Parse the string into a datetime object
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        return date_obj.strftime(format)
    except ValueError:
        return value  # Return the original value if parsing fails

app.jinja_env.filters['datetime'] = format_datetime
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
        cursor.execute('SELECT nome_evento, data FROM evento')
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

        # Exceção de formulário incompleto
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

        # Exceção de senhas incompatíveis
        if senha != confirmarSenha:
            flash('As senhas não coincidem. Tente novamente!', 'warning')
            return redirect(url_for('cadastrar'))

        # Inserindo no bd
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT cpf FROM cliente WHERE cpf = ?', (cpf,))
            cliente = cursor.fetchone()

            if cliente:
                flash('Usuário já existe. Tente novamente!', 'warning')
                return redirect(url_for('cadastrar'))
            else:
                # Insert new cliente with esta_ativo = TRUE
                cursor.execute('INSERT INTO cliente (cpf, nome_cliente, celular, endereco) VALUES (?, ?, ?, ?)', (cpf, nome, celular, endereco))
                conn.commit()
                flash('Cliente cadastrado com sucesso!', 'success')

            # Save the hashed password to the file
            with open('instance/passwords.txt', 'a') as f:
                f.write(f"{cpf},{hashed_senha.decode('utf-8')}\n")

            return redirect(url_for('login'))

    return render_template('html/pages/cliente/formulario-cliente.html')

#PERFIL CLIENTE
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    cpf = session.get('cpf')
    if not cpf:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cpf, nome_cliente, celular, endereco FROM cliente WHERE cpf = ?', (cpf,))
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
            cursor.execute('UPDATE cliente SET nome_cliente = ?, celular = ?, endereco = ? WHERE cpf = ?', (nome, celular, endereco, cpf))
            conn.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('perfil'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cpf, nome_cliente, celular, endereco FROM cliente WHERE cpf = ?', (cpf,))
        cliente = cursor.fetchone()

    return render_template('html/pages/cliente/atualizar.html', cliente=cliente)

@app.route('/cliente/deletar/<cpf>', methods=['POST'])
def deletar_cliente(cpf):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cliente WHERE cpf = ?', (cpf,))
        conn.commit()

    
    login_file_path = 'instance/passwords.txt'
    with open(login_file_path, 'r') as file:
        lines = file.readlines()
    
    with open(login_file_path, 'w') as file:
        for line in lines:
            if not line.startswith(cpf + ','):
                file.write(line)
    
    flash('Cliente deletado com sucesso!', 'success')
    return redirect(url_for('logout'))

@app.route('/cliente/parceiros', methods=['GET'])
def ver_parceiros_cliente():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM parceiro')
        parceiros = cursor.fetchall()

    return render_template('html/pages/cliente/parceiros-cliente.html', parceiros=parceiros)

@app.route('/cliente/mobilia/novo', methods=['GET', 'POST'])

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

        try: 
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO visitacao (data, horario, cliente_cpf) VALUES (?, ?, ?)', (data, horario, cpf))
                conn.commit()
                flash('Agendamento criado com sucesso!', 'success')
        except IntegrityError as e:
            flash(str(e), 'danger')
            return render_template('html/pages/cliente/formulario-agendamento.html')

        except Exception as e:
                flash(f'Erro ao criar o evento: {e}', 'danger')
                return render_template('html/pages/cliente/formulario-agendamento.html')


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

    clientes = get_clientes()  # Ensure clientes is fetched before any potential return

    if request.method == 'POST':
        data = request.form['data_evento']
        horario = request.form['horario_evento']
        nome = request.form['nome_evento']
        tipo = request.form['tipo_evento']
        cliente_cpf = request.form['cliente_evento']

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO evento (data, horario, nome_evento, tipo, cliente_cpf) VALUES (?, ?, ?, ?, ?)', (data, horario, nome, tipo, cliente_cpf))
                conn.commit()
                flash('Evento criado com sucesso!', 'success')
                return redirect(url_for('eventos_admin'))
        except IntegrityError as e:
            flash('Conflito detectado: Já existe um agendamento ou evento neste horário.', 'danger')
        except Exception as e:
            flash(f'Erro ao criar o evento: {e}', 'danger')

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
                    cursor.execute('UPDATE evento SET data = ?, horario = ?, nome_evento = ?, tipo = ?, cliente_cpf = ? WHERE data = ? AND horario = ?', (nova_data, novo_horario, nome, tipo, cliente_cpf, data, horario))
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
                cursor.execute('SELECT evento.data, evento.horario, evento.nome_evento, evento.tipo, cliente.cpf, cliente.nome_cliente FROM evento JOIN cliente ON evento.cliente_cpf = cliente.cpf WHERE evento.data = ? AND evento.horario = ?', (data, horario))
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
        cursor.execute('SELECT pagamento.id_pagto, pagamento.forma_pagto, pagamento.qtd_parcelas, pagamento.evento_data, pagamento.evento_horario, pagamento.valor, pagamento.data_pagto, evento.nome_evento FROM evento JOIN pagamento ON evento_data=data AND evento_horario=horario')
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
        cursor.execute('SELECT data, horario, nome_evento FROM evento')
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
        cursor.execute('SELECT data, horario, nome_evento FROM evento')
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

@app.route('/admin/mobilia', methods=['GET'])
def mobilias_admin():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Fetch all rows
        cursor.execute('SELECT * FROM mobilia')
        mobilias = cursor.fetchall()
        
        # Fetch the total sum of quantidade
        cursor.execute('SELECT SUM(quantidade) FROM mobilia')
        total_quantidade = cursor.fetchone()[0]
        if total_quantidade is None:
            total_quantidade = 0

    return render_template('html/pages/admin/mobilias-admin.html', mobilias=mobilias, total_quantidade=total_quantidade)

@app.route('/admin/mobilias/novo', methods=['GET', 'POST'])
def nova_mobilia_admin():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        quantidade = request.form['quantidade']
        tipo_mobilia = request.form['tipo_mobilia']
        valor = request.form['valor']
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO mobilia (tipo_mobilia, quantidade, valor) VALUES (?, ?, ?)', (tipo_mobilia, quantidade, valor))
                conn.commit()
                flash('Mobília criada com sucesso!', 'success')
                return redirect(url_for('mobilias_admin'))
        except Exception as e:
            flash(f'Erro ao criar o kit mobília: {e}', 'danger')
            return redirect(url_for('nova_mobilia_admin'))

    try:
        mobilias = get_mobilias()
    except Exception as e:
        flash(f'Erro ao buscar mobília: {e}', 'danger')
        mobilias = []

    return render_template('html/pages/admin/formulario-mobilia-admin.html', mobilias=mobilias)

@app.route('/admin/mobilias/editar/<tipo_mobilia>', methods=['GET', 'POST'])
def editar_mobilia_admin(tipo_mobilia):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        quantidade = request.form['quantidade']
        valor = request.form['valor']

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE mobilia SET quantidade = ?, valor = ? WHERE tipo_mobilia = ?', 
                               (quantidade, valor, tipo_mobilia))
                conn.commit()
                flash('Mobília atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar mobília: {e}', 'danger')

        return redirect(url_for('mobilias_admin'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mobilia WHERE tipo_mobilia = ?', (tipo_mobilia,))
            mobilia = cursor.fetchone()
    except Exception as e:
        flash(f'Erro ao buscar o kit de mobília: {e}', 'danger')
        mobilia = []  

    return render_template('html/pages/admin/editar-mobilia-admin.html', mobilia=mobilia)

@app.route('/admin/mobilias/deletar/<tipo_mobilia>', methods=['POST'])
def deletar_mobilia_admin(tipo_mobilia):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM mobilia WHERE tipo_mobilia = ?', (tipo_mobilia,))
            conn.commit()
            flash('Mobília deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar mobília: {e}', 'danger')

    return redirect(url_for('mobilias_admin'))

@app.route('/admin/mobilias/alugueis', methods=['GET'])
def mobilias_alugadas_admin():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT cam.cliente_cpf, cam.tipo_mobilia, cam.qtd_alugada, cam.valor, cam.data_aluguel, c.nome_cliente
                        FROM cliente_aluga_mobilia cam
                        JOIN cliente c ON c.cpf = cam.cliente_cpf
                       ''')
        mobilias_alugadas = cursor.fetchall()
        print(mobilias_alugadas)

    return render_template('html/pages/admin/mobilias-alugadas-admin.html', mobilias_alugadas=mobilias_alugadas)


@app.route('/cliente/mobilias/', methods=['GET', 'POST'])
def mobilias_cliente():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cliente_aluga_mobilia WHERE cliente_aluga_mobilia.cliente_cpf = ?', (session.get('cpf'),))      
        mobilias_cliente = cursor.fetchall()


    return render_template('html/pages/cliente/mobilias-cliente.html', mobilias_cliente=mobilias_cliente)

@app.route('/cliente/mobilias/nova', methods=['GET', 'POST'])
def nova_mobilia_cliente():
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        tipo_mobilia = request.form['tipo_mobilia']
        qtd_alugada = int(request.form['qtd_alugada'])
        data_aluguel = request.form['data_aluguel']
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT quantidade FROM mobilia WHERE tipo_mobilia = ?', (tipo_mobilia,))
                result = cursor.fetchone()
                
                if result is None:
                    flash('Tipo de mobília não encontrado.', 'danger')                            
                    return redirect(url_for('nova_mobilia_cliente'))
                
                quantidade_disponivel = result[0]
                
                if qtd_alugada > quantidade_disponivel:
                    flash('Quantidade solicitada excede a quantidade disponível.', 'danger')
                    return redirect(url_for('nova_mobilia_cliente'))
                
                cursor.execute('SELECT valor FROM mobilia WHERE tipo_mobilia = ?', (tipo_mobilia,))
                valor = cursor.fetchone()[0]

                qtd_alugada_float = float(qtd_alugada)

                valor_total = valor * qtd_alugada_float

                cursor.execute('INSERT INTO cliente_aluga_mobilia (cliente_cpf, tipo_mobilia, qtd_alugada, valor, data_aluguel) VALUES (?, ?, ?, ?, ?)', 
                               (session.get('cpf'), tipo_mobilia, qtd_alugada, valor_total, data_aluguel))
                
                cursor.execute('UPDATE mobilia SET quantidade = quantidade - ? WHERE tipo_mobilia = ?', 
                               (qtd_alugada, tipo_mobilia))

                conn.commit()
                flash('Mobília alugada com sucesso!', 'success')
                return redirect(url_for('mobilias_cliente'))
        except Exception as e:
            flash(f'Erro ao alugar mobília: {e}', 'danger')
            return redirect(url_for('nova_mobilia_cliente'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tipo_mobilia, quantidade FROM mobilia')
            mobilias = cursor.fetchall()
    except Exception as e:
        flash(f'Erro ao buscar mobílias: {e}', 'danger')
        mobilias = []

    return render_template('html/pages/cliente/formulario-mobilia-cliente.html', mobilias=mobilias)

@app.route('/cliente/mobilias/deletar/<tipo_mobilia>', methods=['POST'])
def excluir_mobilia_cliente(tipo_mobilia):
    if not session.get('cpf'):
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT qtd_alugada FROM cliente_aluga_mobilia WHERE cliente_cpf = ? AND tipo_mobilia = ?', 
                           (session.get('cpf'), tipo_mobilia))
            resultado = cursor.fetchone()
            
            if resultado is None:
                flash('Registro de aluguel não encontrado.', 'danger')
                return redirect(url_for('mobilias_cliente'))
            
            qtd_alugada = resultado[0]
            
            cursor.execute('DELETE FROM cliente_aluga_mobilia WHERE cliente_cpf = ? AND tipo_mobilia = ?', 
                           (session.get('cpf'), tipo_mobilia))
            
            cursor.execute('UPDATE mobilia SET quantidade = quantidade + ? WHERE tipo_mobilia = ?', 
                           (qtd_alugada, tipo_mobilia))
            
            conn.commit()
            flash('Mobília devolvida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao devolver mobília: {e}', 'danger')

    return redirect(url_for('mobilias_cliente'))


@app.route('/admin/eventos/relatorio')
def gerar_relatorio_eventos():
    conn = sqlite3.connect('instance/salao_festas.db')

    eventos_df = pd.read_sql_query("SELECT * FROM evento", conn)
    pagamentos_df = pd.read_sql_query("SELECT * FROM pagamento", conn)

    eventos_df['data'] = pd.to_datetime(eventos_df['data'], format='%Y-%m-%d')
    pagamentos_df['evento_data'] = pd.to_datetime(pagamentos_df['evento_data'], infer_datetime_format=True)

    eventos_df['mes'] = eventos_df['data'].dt.to_period('M')

    merged_df = pd.merge(eventos_df, pagamentos_df, left_on=['data', 'horario'], right_on=['evento_data', 'evento_horario'])

    # relatorio 1: eventos por mes
    ocorrencias_evento = eventos_df.groupby(['mes', 'tipo']).size().unstack(fill_value=0)
    ax = ocorrencias_evento.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Convert the PeriodIndex to the desired format
    labels = ocorrencias_evento.index.strftime('%m/%Y')

    ax.set_xlabel('Mês')
    ax.set_ylabel('Número de eventos')
    ax.set_title('Eventos por mês')
    ax.set_xticks(range(len(labels)))  # Set the positions of the ticks
    ax.set_xticklabels(labels, rotation=45)  # Set the formatted labels
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure y-axis labels are integers
    plt.tight_layout()
    plt.savefig('static/ocorrencias_eventos.png')
    plt.close()

    # relatorio2: receita por tipo de evento
    receita_por_tipo_evento = merged_df.groupby('tipo')['valor'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(receita_por_tipo_evento['tipo'], receita_por_tipo_evento['valor'])
    plt.xlabel('Tipo de evento')
    plt.ylabel('Receita')
    plt.title('Receita por tipo de evento')
    plt.xticks(ticks=range(len(receita_por_tipo_evento['tipo'])), labels=receita_por_tipo_evento['tipo'], rotation=45)
    plt.tight_layout()
    plt.savefig('static/receita_por_tipo_evento.png')
    plt.close()

    #relatorio3: total de eventos por mes
    total_eventos_mes = eventos_df.groupby('mes').size()

    # Convert the PeriodIndex to the desired format
    labels = total_eventos_mes.index.strftime('%m/%Y')

    plt.figure(figsize=(10, 6))
    plt.pie(total_eventos_mes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Número total de eventos por mês')
    plt.tight_layout()
    plt.savefig('static/total_eventos_por_mes.png')
    plt.close()

    conn.close()

    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Relatório de Eventos", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Ocorrências de eventos por mês", styles['Heading2']))
    elements.append(Image('static/ocorrencias_eventos.png', width=500, height=300))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Receita por tipo de evento", styles['Heading2']))
    elements.append(Image('static/receita_por_tipo_evento.png', width=500, height=300))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Número total de eventos por mês", styles['Heading2']))
    elements.append(Image('static/total_eventos_por_mes.png', width=500, height=300))
    elements.append(Spacer(1, 12))


    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='relatorio_eventos.pdf', mimetype='application/pdf')

@app.route('/admin/pagamentos/relatorio')
def gerar_relatorio_pagamentos():
    conn = sqlite3.connect('instance/salao_festas.db')

    eventos_df = pd.read_sql_query("SELECT * FROM evento", conn)
    pagamentos_df = pd.read_sql_query("SELECT * FROM pagamento", conn)

    eventos_df['data'] = pd.to_datetime(eventos_df['data'], format='%Y-%m-%d')
    pagamentos_df['evento_data'] = pd.to_datetime(pagamentos_df['evento_data'], infer_datetime_format=True)
    pagamentos_df['data_pagto'] = pd.to_datetime(pagamentos_df['data_pagto'], infer_datetime_format=True)

    eventos_df['mes'] = eventos_df['data'].dt.to_period('M')
    pagamentos_df['mes'] = pagamentos_df['data_pagto'].dt.to_period('M')

    merged_df = pd.merge(eventos_df, pagamentos_df, left_on=['data', 'horario'], right_on=['evento_data', 'evento_horario'])

    merged_df['mes'] = merged_df['data_pagto'].dt.to_period('M')

    valores = merged_df.groupby('mes')['valor'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.plot(valores['mes'].dt.strftime('%m/%Y'), valores['valor'], marker='o')
    plt.xlabel('Mês')
    plt.ylabel('Valor pago')
    plt.title('Valores pagos por mês')
    plt.xticks(rotation=45)
    plt.ylim(0, valores['valor'].max() + 50)  
    plt.yticks(range(0, int(valores['valor'].max() + 50), 50))
    plt.tight_layout()
    plt.savefig('static/valores_pagos.png')
    plt.close()

    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Relatório de Pagamentos", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Valores pagos por mês", styles['Heading2']))
    elements.append(Image('static/valores_pagos.png', width=500, height=300))
    elements.append(Spacer(1, 12))

    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='relatorio_pagamentos.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)