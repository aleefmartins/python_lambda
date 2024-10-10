import json
import re
from datetime import datetime

# Listas de possíveis nomes para cada tipo de campo
POSSIBLE_EMAIL_KEYS = ["email", "email_address", "mail"]
POSSIBLE_PHONE_KEYS = ["telefone", "phone", "phone_number", "mobile", "contact_number"]
POSSIBLE_CNPJ_KEYS = ["cnpj", "cnpj_da_empresa", "company_cnpj"]
POSSIBLE_NAME_KEYS = ["nome", "name", "first_name"]
POSSIBLE_LAST_NAME_KEYS = ["sobrenome", "lastname", "last_name"]

# Expressões regulares para validação
CNPJ_REGEX = r"^\d{14}$"  # CNPJ sem pontuação deve ter exatamente 14 dígitos
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?\d{11,15}$"

def clean_cnpj(cnpj):
    """
    Remove caracteres especiais do CNPJ, como pontos, barras e traços.
    """
    return re.sub(r"[\.\-\/]", "", cnpj)

def extract_from_fields(data):
    """
    Extrai informações dos campos de um payload específico, como mostrado no exemplo da imagem.
    """
    emails = []
    phones = []
    cnpjs = []
    names = []
    last_names = []

    if isinstance(data, dict) and "field_name" in data:
        # Iterar sobre a lista de campos
        for field in data["field_name"]:
            if isinstance(field, dict):
                field_name = field.get("name", "").lower()
                values = field.get("values", [])

                # Verificar se é um possível campo de email
                if field_name in POSSIBLE_EMAIL_KEYS and values:
                    emails.extend(values)

                # Verificar se é um possível campo de telefone
                if field_name in POSSIBLE_PHONE_KEYS and values:
                    phones.extend(values)

                # Verificar se é um possível campo de CNPJ
                if field_name in POSSIBLE_CNPJ_KEYS and values:
                    cnpjs.extend(values)

                # Verificar se é um possível campo de nome
                if field_name in POSSIBLE_NAME_KEYS and values:
                    names.extend(values)

                # Verificar se é um possível campo de sobrenome
                if field_name in POSSIBLE_LAST_NAME_KEYS and values:
                    last_names.extend(values)

    return emails, phones, cnpjs, names, last_names

def extract_contact_info(data):
    """
    Função recursiva para extrair informações de contato (email, telefone, CNPJ, nome e sobrenome) de payloads variados.
    """
    emails = []
    phones = []
    cnpjs = []
    names = []
    last_names = []

    # Se for um dicionário, percorre os campos
    if isinstance(data, dict):
        # Verifica se é uma estrutura no formato específico de fields
        extracted_emails, extracted_phones, extracted_cnpjs, extracted_names, extracted_last_names = extract_from_fields(data)
        emails.extend(extracted_emails)
        phones.extend(extracted_phones)
        cnpjs.extend(extracted_cnpjs)
        names.extend(extracted_names)
        last_names.extend(extracted_last_names)

        # Para outros casos, percorre as chaves normalmente
        for key, value in data.items():
            # Se o valor for uma lista ou dicionário, aplica a função recursivamente
            if isinstance(value, (dict, list)):
                sub_emails, sub_phones, sub_cnpjs, sub_names, sub_last_names = extract_contact_info(value)
                emails.extend(sub_emails)
                phones.extend(sub_phones)
                cnpjs.extend(sub_cnpjs)
                names.extend(sub_names)
                last_names.extend(sub_last_names)

    # Se for uma lista, itera sobre os elementos
    elif isinstance(data, list):
        for item in data:
            sub_emails, sub_phones, sub_cnpjs, sub_names, sub_last_names = extract_contact_info(item)
            emails.extend(sub_emails)
            phones.extend(sub_phones)
            cnpjs.extend(sub_cnpjs)
            names.extend(sub_names)
            last_names.extend(sub_last_names)

    return emails, phones, cnpjs, names, last_names

def validate_cnpj(cnpj):
    """
    Valida se o CNPJ segue o formato correto de 14 dígitos.
    """
    # Remove pontuação e valida se tem 14 dígitos
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
        # Divide o caminho em partes e pega a última seção como origem
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

def lambda_handler(event, context):
    """
    Função principal da AWS Lambda que será chamada com o evento.
    """
    try:
        # Parse do body recebido (pode vir de um evento HTTP)
        body = event.get('body')
        if body:
            data = json.loads(body)
        else:
            data = event

        # Extrair informações de contato
        emails, phones, cnpjs, names, last_names = extract_contact_info(data)

        # Capturar o caminho do evento para definir a origem
        path = event.get("path", "")
        origin = get_origin_from_path(path)

        # Capturar a data atual no formato brasileiro (24 horas)
        current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Validações para cada tipo de dado
        email_valido = all(validate_email(email) for email in emails)
        telefone_valido = all(validate_phone(phone) for phone in phones)
        
        # Validação de CNPJ e remoção de pontuações
        cnpj_valido, cnpjs_cleaned = zip(*[validate_cnpj(cnpj) for cnpj in cnpjs])

        # Calcular o rating com base nas validações
        rating = calculate_rating(email_valido, telefone_valido, all(cnpj_valido))

        # Resposta com as informações encontradas e validações
        return {
            'statusCode': 200,
            'body': json.dumps({
                'emails': emails,
                'phones': phones,
                'cnpjs': list(cnpjs_cleaned),  # Retorna CNPJs sem pontuação
                'names': names,
                'last_names': last_names,
                'data': current_datetime,
                'origem': origin,
                'email_valido': email_valido,
                'telefone_valido': telefone_valido,
                'cnpj_valido': all(cnpj_valido),
                'rating': rating
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Erro ao processar o payload',
                'error': str(e)
            })
        }
