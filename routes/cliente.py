from flask import Blueprint, render_template

cliente_route = Blueprint('cliente', __name__)

"""
    Rota de clientes
    - /clientes/ {GET} -> lista todos os clientes
    - /clientes/ {POST} -> inserir o cliente no banco de dados
    - /clientes/novo {GET} -> renderizar um formulario para criar um novo cliente
    - /clientes/<id_cliente> {GET} -> obter um cliente pelo id
    - /clientes/<id_cliente>/editar {GET} -> renderizar um formulario para editar um cliente
    - /clientes/<id_cliente>/atualizar {PUT} -> deletar um cliente pelo id
    - /clientes/<id_cliente>/deletar {DELETE} -> deletar um cliente pelo id

"""

@cliente_route.route('/')
def lista_clientes():
    """ lista todos os clientes"""
    return render_template('lista_clientes.html')

@cliente_route.route('/', methods=['POST'])
def inserir_cliente():
    """ inserir os dados de um cliente no banco de dados"""
    pass

@cliente_route.route('/novo')
def form_cliente():
    """ formulario para cadastrar um cliente"""
    return render_template('form_cliente.html')


@cliente_route.route('/<int:id_cliente>')
def detalhe_cliente(id_cliente):
    """ exibir detalhes de um cliente"""
    return render_template('detalhe_cliente.html')

@cliente_route.route('/<int:id_cliente>/editar')
def form_editar_cliente(id_cliente):
    """ formulario para editar um cliente """
    return render_template('form_editar_cliente.html')

@cliente_route.route('/<int:id_cliente>/atualizar', methods=['PUT'])
def atualizar_cliente(id_cliente):
    """ atualizar os dados de um cliente"""
    pass

@cliente_route.route('/<int:id_cliente>/deletar', methods=['DELETE'])
def deletar_cliente(id_cliente):
    """ deletar um cliente """
    pass