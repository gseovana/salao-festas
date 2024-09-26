import sqlite3
from faker import Faker
import random
import os

fake = Faker()

#db_path = os.path.abspath('instance/salao_festas.db')

#conn = sqlite3.connect(db_path)
#cursor = conn.cursor()

conn = sqlite3.connect(r'C:\Users\geova\Documents\UFOP\4° período\salao-festas\salao-festas\instance\salao_festas.db')
#conn = sqlite3.connect('/salao-festas/instance/salao_festas.db')
cursor = conn.cursor()

# Função para obter valores já existentes em outras tabelas (ex.: CPF de clientes)
def get_existing_cpfs():
    cursor.execute('SELECT cpf FROM cliente')
    return [row[0] for row in cursor.fetchall()]

def get_existing_eventos():
    cursor.execute('SELECT data, horario FROM evento')
    return [(row[0], row[1]) for row in cursor.fetchall()]

def get_existing_tipo_mobilia():
    cursor.execute('SELECT tipo_mobilia FROM mobilia')
    return [row[0] for row in cursor.fetchall()]

def inserir_clientes(n):
    for _ in range(n):
        cpf = str(fake.random_int(min=10000000000, max=99999999999))  # 11 dígitos como string
        formatted_cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        nome_cliente = fake.name()
        celular = fake.phone_number()
        endereco = fake.address().replace('\n', ', ')
        cursor.execute('INSERT INTO cliente (cpf, nome_cliente, celular, endereco) VALUES (?, ?, ?, ?)',
                       (formatted_cpf, nome_cliente, celular, endereco))
    conn.commit()

def inserir_visitacoes(n):
    cpfs = get_existing_cpfs()
    for _ in range(n):
        data = fake.date_between(start_date='today', end_date='+30d')
        horario = fake.time(pattern="%H:%M")
        cliente_cpf = random.choice(cpfs)
        cursor.execute('INSERT INTO visitacao (data, horario, cliente_cpf) VALUES (?, ?, ?)',
                       (data, horario, cliente_cpf))
    conn.commit()

def inserir_eventos(n):
    cpfs = get_existing_cpfs()
    for _ in range(n):
        data = fake.date_between(start_date='today', end_date='+30d')
        horario = fake.time(pattern="%H:%M")
        nome_evento = fake.sentence(nb_words=3)
        tipo = random.choice(['Casamento', 'Aniversário', 'Corporativo', 'Formatura', 'Debutante', 'Batizado', 'Confraternização', 'Cultural', 'Outros'])
        cliente_cpf = random.choice(cpfs)
        cursor.execute('INSERT INTO evento (data, horario, nome_evento, tipo, cliente_cpf) VALUES (?, ?, ?, ?, ?)',
                       (data, horario, nome_evento, tipo, cliente_cpf))
    conn.commit()

def inserir_pagamentos(n):
    eventos = get_existing_eventos()
    for _ in range(n):
        if not eventos:
            break
        evento_data, evento_horario = random.choice(eventos)
        forma_pagto = random.choice(['Cartão', 'Dinheiro'])
        qtd_parcelas = random.randint(1, 3)
        valor = round(random.uniform(10.0, 1000.0), 2)
        data_pagto = fake.date_this_month()
        cursor.execute('INSERT INTO pagamento (forma_pagto, qtd_parcelas, evento_data, evento_horario, valor, data_pagto) VALUES (?, ?, ?, ?, ?, ?)',
                       (forma_pagto, qtd_parcelas, evento_data, evento_horario, valor, data_pagto))
    conn.commit()

def inserir_mobilia(n):
    for _ in range(n):
        tipo_mobilia = random.choice(['Mesa', 'Cadeira', 'Sofá', 'Mesa de Centro', 'Mesas de Buffet', 'Banco', 'Cadeira de Madeira', 'Cadeira Estofada', 'Tabela de Doces', 'Tenda', 'Palco', 'Estrado', 'Carro de Apoio', 'Parques Infantis', 'Brinquedos', 'Mesa de Som', 'Iluminação', 'Decoração', 'Mesa para Drinks', 'Quiosque'
])
        quantidade = random.randint(1, 100)
        valor = round(random.uniform(5.0, 500.0), 2)
        cursor.execute('INSERT INTO mobilia (tipo_mobilia, quantidade, valor) VALUES (?, ?, ?)',
                       (tipo_mobilia, quantidade, valor))
    conn.commit()

def inserir_clientes_aluga_mobilia(qtd):
    lista_cpfs = get_existing_cpfs()
    for _ in range(qtd):
        cliente_cpf = random.choice(lista_cpfs)
        tipo_mobilia = random.choice(['Cadeiras', 'Mesas', 'Louças'])
        qtd_alugada = random.randint(1, 10)
        valor = random.uniform(50, 500)
        data_aluguel = fake.date_this_year()
        
        # Verificar se já existe essa combinação de cliente e mobília
        cursor.execute('SELECT * FROM cliente_aluga_mobilia WHERE cliente_cpf = ? AND tipo_mobilia = ?', (cliente_cpf, tipo_mobilia))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"Combinação existente para CPF {cliente_cpf} e tipo de mobília {tipo_mobilia}. Ignorando inserção.")
        else:
            cursor.execute(
                'INSERT INTO cliente_aluga_mobilia (cliente_cpf, tipo_mobilia, qtd_alugada, valor, data_aluguel) VALUES (?, ?, ?, ?, ?)',
                (cliente_cpf, tipo_mobilia, qtd_alugada, valor, data_aluguel)
            )
            print(f"Inserido: CPF {cliente_cpf}, Tipo de mobília: {tipo_mobilia}")

    conn.commit()
def inserir_parceiros(n):
    for _ in range(n):
        nome = fake.name()
        celular = fake.phone_number()
        cursor.execute('INSERT INTO parceiro (nome, celular) VALUES (?, ?)', (nome, celular))
    conn.commit()

# Preenchimento das tabelas
inserir_clientes(25)
inserir_parceiros(10)
inserir_mobilia(10)
inserir_visitacoes(25)
inserir_eventos(25)
inserir_pagamentos(25)
inserir_clientes_aluga_mobilia(25)

conn.close()
