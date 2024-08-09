from flask import Blueprint

cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
def home():
    return 'Página cliente'

