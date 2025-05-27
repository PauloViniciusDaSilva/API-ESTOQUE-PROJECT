# Importando as bibliotecas necessárias para o funcionamento da API
from flask import Flask, request, jsonify  # Flask para criar a API, request para pegar dados enviados, jsonify para respostas JSON
import json  # Para manipular arquivos JSON
import os  # Para verificar existência de arquivos no sistema

# Criando a aplicação Flask
app = Flask(__name__)

# Definindo o nome do arquivo JSON onde os dados serão armazenados
DATA_FILE = 'estoque.json'

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    # Verifica se o arquivo existe no diretório
    if os.path.exists(DATA_FILE):
        # Abre o arquivo no modo leitura ('r')
        with open(DATA_FILE, 'r') as f:
            # Carrega o conteúdo JSON e retorna como uma lista de produtos
            return json.load(f)
    else:
        # Caso o arquivo não exista, retorna uma lista vazia (sem produtos)
        return []

# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    # Abre o arquivo no modo escrita ('w'), sobrescrevendo o conteúdo anterior
    with open(DATA_FILE, 'w') as f:
        # Converte a lista de produtos para formato JSON e salva no arquivo, com identação para melhor leitura
        json.dump(dados, f, indent=4)

# Rota para listar todos os produtos cadastrados (método GET)
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    # Carrega os produtos existentes do arquivo
    produtos = carregar_dados()
    # Retorna a lista de produtos em formato JSON com status HTTP 200 (OK)
    return jsonify(produtos), 200

# Rota para buscar um produto específico pelo seu ID (método GET)
@app.route('/produtos/<int:id>', methods=['GET'])
def buscar_produto(id):
    # Carrega a lista completa de produtos
    produtos = carregar_dados()
    # Percorre a lista para encontrar um produto com o ID solicitado
    for produto in produtos:
        if produto['id'] == id:
            # Caso encontrado, retorna o produto em JSON e status 200 (OK)
            return jsonify(produto), 200
    # Se não encontrar o produto, retorna mensagem de erro com status 404 (não encontrado)
    return jsonify({'erro': 'Produto não encontrado'}), 404

# Rota para adicionar um novo produto ao estoque (método POST)
@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    # Carrega a lista atual de produtos para atualizar depois
    produtos = carregar_dados()
    # Obtém os dados enviados no corpo da requisição no formato JSON
    dados = request.get_json()

    # Validação dos dados enviados

    # Verifica se os dados foram enviados (não nulo)
    if dados is None:
        return jsonify({'erro': 'Parâmetro vazio: nenhum dado enviado'}), 400

    # Verifica se o campo 'nome' foi informado
    if 'nome' not in dados:
        return jsonify({'erro': 'Parâmetro "nome" não informado'}), 400
    # Verifica se o 'nome' é uma string não vazia (exclui espaços)
    if not isinstance(dados['nome'], str) or dados['nome'].strip() == '':
        return jsonify({'erro': 'Parâmetro "nome" inválido ou vazio'}), 400

    # Verifica se o campo 'quantidade' foi informado
    if 'quantidade' not in dados:
        return jsonify({'erro': 'Parâmetro "quantidade" não informado'}), 400
    # Tenta converter o valor para inteiro, verificando se é válido
    try:
        quantidade = int(dados['quantidade'])
        # Quantidade deve ser maior ou igual a zero
        if quantidade < 0:
            return jsonify({'erro': 'Parâmetro "quantidade" deve ser número inteiro não negativo'}), 400
    except (ValueError, TypeError):
        # Se falhar a conversão, retorna erro de número inválido
        return jsonify({'erro': 'Parâmetro "quantidade" não é um número inteiro válido'}), 400

    # Verifica se o campo 'preco' foi informado
    if 'preco' not in dados:
        return jsonify({'erro': 'Parâmetro "preco" não informado'}), 400
    # Tenta converter o valor para float, verificando se é válido
    try:
        preco = float(dados['preco'])
        # Preço também não pode ser negativo
        if preco < 0:
            return jsonify({'erro': 'Parâmetro "preco" deve ser número não negativo'}), 400
    except (ValueError, TypeError):
        # Caso não seja um número válido, retorna erro
        return jsonify({'erro': 'Parâmetro "preco" não é um número válido'}), 400

    # Gerar um novo ID automático para o produto
    # Busca o maior ID atual na lista de produtos, ou 0 se lista estiver vazia, e soma 1
    novo_id = max([p['id'] for p in produtos], default=0) + 1

    # Monta o novo produto com os dados validados
    novo_produto = {
        'id': novo_id,
        'nome': dados['nome'].strip(),  # Remove espaços desnecessários do nome
        'quantidade': quantidade,
        'preco': preco
    }

    # Adiciona o novo produto à lista de produtos
    produtos.append(novo_produto)
    try:
        # Salva a lista atualizada no arquivo JSON
        salvar_dados(produtos)
    except Exception:
        # Caso haja erro ao salvar, retorna mensagem de erro 500 (erro interno)
        return jsonify({'erro': 'Não foi possível executar a função de salvar os dados'}), 500

    # Retorna o produto criado com status 201 (Criado)
    return jsonify(novo_produto), 201

# Rota para atualizar dados de um produto existente pelo ID (método PUT)
@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    # Carrega a lista atual de produtos
    produtos = carregar_dados()
    # Obtém os dados enviados no corpo da requisição (JSON)
    dados = request.get_json()

    # Verifica se algum dado foi enviado para atualização
    if dados is None:
        return jsonify({'erro': 'Parâmetro vazio: nenhum dado enviado'}), 400

    # Percorre a lista para encontrar o produto pelo ID
    for produto in produtos:
        if produto['id'] == id:
            # Se o campo 'nome' foi enviado, valida e atualiza
            if 'nome' in dados:
                if not isinstance(dados['nome'], str) or dados['nome'].strip() == '':
                    return jsonify({'erro': 'Parâmetro "nome" inválido ou vazio'}), 400
                produto['nome'] = dados['nome'].strip()

            # Se o campo 'quantidade' foi enviado, tenta validar e atualizar
            if 'quantidade' in dados:
                try:
                    quantidade = int(dados['quantidade'])
                    if quantidade < 0:
                        return jsonify({'erro': 'Parâmetro "quantidade" deve ser número inteiro não negativo'}), 400
                    produto['quantidade'] = quantidade
                except (ValueError, TypeError):
                    return jsonify({'erro': 'Parâmetro "quantidade" não é um número inteiro válido'}), 400

            # Se o campo 'preco' foi enviado, tenta validar e atualizar
            if 'preco' in dados:
                try:
                    preco = float(dados['preco'])
                    if preco < 0:
                        return jsonify({'erro': 'Parâmetro "preco" deve ser número não negativo'}), 400
                    produto['preco'] = preco
                except (ValueError, TypeError):
                    return jsonify({'erro': 'Parâmetro "preco" não é um número válido'}), 400

            try:
                # Tenta salvar os dados atualizados no arquivo JSON
                salvar_dados(produtos)
            except Exception:
                # Retorna erro 500 se não conseguir salvar
                return jsonify({'erro': 'Não foi possível executar a função de salvar os dados'}), 500

            # Retorna o produto atualizado com status 200 (OK)
            return jsonify(produto), 200

    # Caso o produto com ID não seja encontrado, retorna erro 404
    return jsonify({'erro': 'Produto não encontrado'}), 404

# Rota para deletar um produto pelo ID (método DELETE)
@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    # Carrega a lista atual de produtos
    produtos = carregar_dados()
    # Cria uma nova lista filtrando o produto com o ID a ser deletado
    produtos_filtrados = [p for p in produtos if p['id'] != id]

    # Se a lista filtrada tem o mesmo tamanho, significa que o produto não existia
    if len(produtos) == len(produtos_filtrados):
        return jsonify({'erro': 'Produto não encontrado'}), 404

    try:
        # Salva a lista atualizada sem o produto deletado
        salvar_dados(produtos_filtrados)
    except Exception:
        # Retorna erro 500 caso falhe salvar os dados
        return jsonify({'erro': 'Não foi possível executar a função de salvar os dados'}), 500

    # Retorna mensagem de sucesso ao deletar com status 200 (OK)
    return jsonify({'mensagem': 'Produto deletado com sucesso'}), 200

# Rota raiz apenas para verificar se a API está funcionando
@app.route('/', methods=['GET'])
def home():
    # Retorna mensagem simples confirmando que a API está rodando
    return jsonify({'mensagem': 'API de Controle de Estoque funcionando!'}), 200

# Ponto de entrada do script para rodar a aplicação Flask em modo debug
if __name__ == '__main__':
    app.run(debug=True)
