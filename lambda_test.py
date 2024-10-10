import json
from lambda_function import lambda_handler  # Substitua por 'lambda_function' se o nome do arquivo principal for 'lambda_function.py'

# Exemplo de evento que será passado para a Lambda (usando a estrutura do payload de exemplo)
test_event = {
    "body": json.dumps({
        "field_name": [
            { "name": "cnpj_da_empresa", "values": ["12345678901234"] },
            { "name": "nome", "values": ["João"] },
            { "name": "sobrenome", "values": ["Silva"] },
            { "name": "email", "values": ["joao.silva@empresa.com"] },
            { "name": "telefone", "values": ["+5511999999999"] }
        ]
    }),
    "path": "/instagram"
}

# Chamando a função lambda_handler com um evento de teste
response = lambda_handler(test_event, None)

# Imprimir o resultado para verificar a saída
print("Resposta da Lambda:")
print(json.dumps(response, indent=4))
