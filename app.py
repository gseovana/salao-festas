import secrets
import bcrypt
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
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
        cursor.execute('SELECT * FROM visitacao')
        games = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return games

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
                    return redirect(url_for('adminpage'))  
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
            except:
                    flash('Erro ao cadastrar cliente. Tente novamente!', 'error')

    return render_template('html/pages/cliente/cadastrar.html')

#PERFIL CLIENTE
@app.route('/cliente/perfil', methods=['GET', 'POST'])
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

    return render_template('html/pages/cliente/perfil-cliente.html', cliente=cliente)

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
        for agendamento in agendamentos:
            print(agendamento)  # Debug statement

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
        hora = request.form['hora']

        if data == "":
            flash('Preencha o campo Data!', 'warning')
        elif hora == "":
            flash('Preencha o campo Hora!', 'warning')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO visitacao (data, horario, cliente_cpf) VALUES (?, ?, ?)', (data, hora, cpf))
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
    hora_agendamento = request.form.get('hora')


    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM visitacao WHERE data=? AND horario=?', (data_agendamento, hora_agendamento))
        conn.commit()

    flash('Agendamento deletado com sucesso!', 'success')
    return redirect(url_for('agendamentos_cliente'))

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