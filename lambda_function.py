import json
import re
import boto3
from datetime import datetime

# Configuração do S3
S3_BUCKET_NAME = "leadsalef"  # Substitua pelo nome do seu bucket
S3_OUTPUT_PREFIX = "leads/"  # Diretório de saída no bucket S3

# Inicialização do cliente S3
s3_client = boto3.client('s3')

# Expressões regulares para validação
CNPJ_REGEX = r"^\d{14}$"
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?\d{11,15}$"

# Listas de possíveis nomes para cada tipo de campo
POSSIBLE_EMAIL_KEYS = ["email", "email_address", "mail"]
POSSIBLE_PHONE_KEYS = ["telefone", "phone", "phone_number", "mobile", "contact_number"]
POSSIBLE_CNPJ_KEYS = ["cnpj", "cnpj_da_empresa", "company_cnpj"]
POSSIBLE_NAME_KEYS = ["nome", "name", "first_name"]
POSSIBLE_LAST_NAME_KEYS = ["sobrenome", "lastname", "last_name"]


def clean_cnpj(cnpj):
    """
    Remove caracteres especiais do CNPJ, como pontos, barras e traços.
    """
    return re.sub(r"[\.\-\/]", "", cnpj)


def validate_cnpj(cnpj):
    """
    Valida se o CNPJ segue o formato correto de 14 dígitos, mesmo com pontuação.
    """
    cleaned_cnpj = clean_cnpj(cnpj)
    return bool(re.match(CNPJ_REGEX, cleaned_cnpj)), cleaned_cnpj


def validate_email(email):
    """
    Valida o formato do email usando regex.
    """
    return bool(re.match(EMAIL_REGEX, email))


def validate_phone(phone):
    """
    Valida o formato do telefone com base no padrão de 11 a 15 dígitos (com ou sem +).
    """
    return bool(re.match(PHONE_REGEX, phone))


def get_origin_from_path(path):
    """
    Extrai o nome da origem a partir do caminho da requisição (endpoint).
    """
    if path:
        return path.strip('/').split('/')[-1]
    return "desconhecido"


def calculate_rating(email_valido, telefone_valido, cnpj_valido):
    """
    Calcula o rating com base na qualidade do lead:
    - 2 = Todos válidos
    - 1 = Pelo menos 1 válido
    - 0 = Nenhum válido
    """
    valid_fields = sum([email_valido, telefone_valido, cnpj_valido])
    if valid_fields == 3:
        return 2
    elif valid_fields >= 1:
        return 1
    else:
        return 0


def save_to_s3(bucket_name, file_key, data):
    """
    Salva ou atualiza o payload recebido no bucket S3 em formato JSON.
    """
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=json.dumps(data))
    print(f"Dados salvos no S3 em: s3://{bucket_name}/{file_key}")


def load_existing_data(bucket_name, file_key):
    """
    Carrega os dados existentes no arquivo S3 se o arquivo já existir.
    Caso não exista, retorna uma lista vazia.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        existing_data = json.loads(response['Body'].read().decode('utf-8'))
        return existing_data
    except s3_client.exceptions.NoSuchKey:
        # Se o arquivo não existir, retorna uma lista vazia para começar um novo arquivo
        return []


def extract_contact_info(data):
    """
    Extrai as informações de contato dos campos fornecidos e retorna os valores encontrados.
    """
    emails = []
    phones = []
    cnpjs = []
    names = []
    last_names = []

    if isinstance(data, dict) and "field_name" in data:
        for field in data["field_name"]:
            field_name = field.get("name", "").lower()
            values = field.get("values", [])

            if field_name in POSSIBLE_EMAIL_KEYS and values:
                emails.extend(values)
            if field_name in POSSIBLE_PHONE_KEYS and values:
                phones.extend(values)
            if field_name in POSSIBLE_CNPJ_KEYS and values:
                cnpjs.extend(values)
            if field_name in POSSIBLE_NAME_KEYS and values:
                names.extend(values)
            if field_name in POSSIBLE_LAST_NAME_KEYS and values:
                last_names.extend(values)

    return emails, phones, cnpjs, names, last_names


def lambda_handler(event, context):
    """
    Função principal que será executada pela Lambda.
    """
    try:
        # Capturar o payload recebido pelo webhook
        body = event.get('body')
        if body:
            data = json.loads(body)
        else:
            data = event

        # Extração de informações de contato
        emails, phones, cnpjs, names, last_names = extract_contact_info(data)

        # Capturar o caminho do evento para definir a origem
        path = event.get("path", "")
        origin = get_origin_from_path(path)

        # Capturar a data atual no formato brasileiro (24 horas)
        current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Validações de cada campo
        email_valido = all(validate_email(email) for email in emails)
        telefone_valido = all(validate_phone(phone) for phone in phones)
        cnpj_valido, cnpjs_cleaned = zip(*[validate_cnpj(cnpj) for cnpj in cnpjs])

        # Calcular rating com base na validade dos dados
        rating = calculate_rating(email_valido, telefone_valido, all(cnpj_valido))

        # Montar o objeto processado com as informações finais
        processed_lead = {
            'emails': emails,
            'phones': phones,
            'cnpjs': list(cnpjs_cleaned),
            'names': names,
            'last_names': last_names,
            'data': current_datetime,
            'origem': origin,
            'email_valido': email_valido,
            'telefone_valido': telefone_valido,
            'cnpj_valido': all(cnpj_valido),
            'rating': rating
        }

        # Gerar o nome do arquivo com base na data atual
        current_date = datetime.now().strftime('%Y-%m-%d')  # Formato: '2024-10-10'
        file_key = f"{S3_OUTPUT_PREFIX}leads_{current_date}.json"

        # Carregar os dados existentes no arquivo para o dia atual (se já existir)
        existing_leads = load_existing_data(S3_BUCKET_NAME, file_key)

        # Adicionar o novo lead à lista de leads existentes
        existing_leads.append(processed_lead)

        # Salvar a lista atualizada de leads no S3
        save_to_s3(S3_BUCKET_NAME, file_key, existing_leads)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Dados processados e salvos com sucesso no S3 para {current_date}',
                's3_location': f"s3://{S3_BUCKET_NAME}/{file_key}"
            })
        }

    except Exception as e:
        # Em caso de erro, retornar a mensagem de falha
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Erro ao salvar os dados no S3',
                'error': str(e)
            })
        }
