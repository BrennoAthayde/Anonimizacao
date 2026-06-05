from faker import Faker
import mysql.connector
import random
from tqdm import tqdm
from datetime import datetime, timedelta

fake = Faker('pt_BR')

#Teste
# CONEXÃO MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="C0rpDBTcc@",
    database="megastore"
)

cursor = conn.cursor()

# -----------------------------
# DEPARTAMENTOS
# -----------------------------

departamentos = [
    'Financeiro',
    'RH',
    'TI',
    'Vendas',
    'Logística',
    'Compras',
    'Marketing'
]

for dep in departamentos:
    cursor.execute(
        "INSERT INTO departamentos (nome_departamento) VALUES (%s)",
        (dep,)
    )

# -----------------------------
# CARGOS
# -----------------------------

cargos = [
    ('Analista', 4500),
    ('Gerente', 9000),
    ('Assistente', 2500),
    ('Supervisor', 6000),
    ('Vendedor', 3200),
    ('Caixa', 2200),
]

for cargo, salario in cargos:
    cursor.execute(
        "INSERT INTO cargos (nome_cargo, salario_base) VALUES (%s,%s)",
        (cargo, salario)
    )

# -----------------------------
# CLIENTES
# -----------------------------

print("Inserindo clientes...")

for _ in tqdm(range(10000)):

    nome = fake.name()
    cpf = fake.unique.cpf()
    rg = str(random.randint(1000000, 9999999))
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=80)
    genero = random.choice(['Masculino', 'Feminino'])
    email = fake.email()
    telefone = fake.phone_number()
    renda = round(random.uniform(1200, 25000), 2)

    cursor.execute("""
        INSERT INTO clientes
        (
            nome_completo,
            cpf,
            rg,
            data_nascimento,
            genero,
            email,
            telefone,
            renda_mensal
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        nome,
        cpf,
        rg,
        nascimento,
        genero,
        email,
        telefone,
        renda
    ))

conn.commit()

# -----------------------------
# FUNCIONÁRIOS
# -----------------------------

print("Inserindo funcionários...")

for _ in tqdm(range(500)):

    nome = fake.name()
    cpf = fake.unique.cpf()
    rg = str(random.randint(1000000, 9999999))
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=65)
    email = fake.company_email()
    telefone = fake.phone_number()
    salario = round(random.uniform(1800, 15000), 2)

    id_departamento = random.randint(1, 7)
    id_cargo = random.randint(1, 6)

    data_admissao = fake.date_between(
        start_date='-10y',
        end_date='today'
    )

    cursor.execute("""
        INSERT INTO funcionarios
        (
            id_departamento,
            id_cargo,
            nome_completo,
            cpf,
            rg,
            data_nascimento,
            email_corporativo,
            telefone,
            salario,
            data_admissao
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        id_departamento,
        id_cargo,
        nome,
        cpf,
        rg,
        nascimento,
        email,
        telefone,
        salario,
        data_admissao
    ))

conn.commit()

# -----------------------------
# FORNECEDORES
# -----------------------------

print("Inserindo fornecedores...")

for _ in range(300):

    cursor.execute("""
        INSERT INTO fornecedores
        (
            razao_social,
            nome_fantasia,
            cnpj,
            email,
            telefone,
            cep,
            cidade,
            estado
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        fake.company(),
        fake.company(),
        fake.unique.cnpj(),
        fake.company_email(),
        fake.phone_number(),
        fake.postcode(),
        fake.city(),
        fake.estado_sigla()
    ))

conn.commit()

# -----------------------------
# CATEGORIAS
# -----------------------------

categorias = [
    'Eletrônicos',
    'Informática',
    'Móveis',
    'Roupas',
    'Ferramentas',
    'Brinquedos',
    'Mercado',
    'Celulares'
]

for cat in categorias:

    cursor.execute("""
        INSERT INTO categorias_produtos
        (nome_categoria)
        VALUES (%s)
    """, (cat,))

conn.commit()

# -----------------------------
# PRODUTOS
# -----------------------------

print("Inserindo produtos...")

for _ in tqdm(range(5000)):

    categoria = random.randint(1, 8)
    fornecedor = random.randint(1, 300)

    preco_custo = round(random.uniform(10, 3000), 2)

    preco_venda = round(
        preco_custo * random.uniform(1.1, 2.5),
        2
    )

    cursor.execute("""
        INSERT INTO produtos
        (
            id_categoria,
            id_fornecedor,
            nome_produto,
            marca,
            codigo_barras,
            preco_custo,
            preco_venda
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        categoria,
        fornecedor,
        fake.word().upper(),
        fake.company(),
        fake.unique.ean13(),
        preco_custo,
        preco_venda
    ))

conn.commit()

# -----------------------------
# CAIXAS
# -----------------------------

for i in range(1, 21):

    cursor.execute("""
        INSERT INTO caixas
        (
            numero_caixa,
            descricao
        )
        VALUES (%s,%s)
    """, (
        i,
        f'Caixa {i}'
    ))

conn.commit()

# -----------------------------
# VENDAS
# -----------------------------

print("Inserindo vendas...")

for _ in tqdm(range(50000)):

    cliente = random.randint(1, 10000)
    funcionario = random.randint(1, 500)
    caixa = random.randint(1, 20)

    valor = round(random.uniform(50, 5000), 2)

    data_venda = fake.date_time_between(
        start_date='-2y',
        end_date='now'
    )

    cursor.execute("""
        INSERT INTO vendas
        (
            id_cliente,
            id_funcionario,
            id_caixa,
            data_venda,
            valor_total,
            desconto,
            cpf_na_nota
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        cliente,
        funcionario,
        caixa,
        data_venda,
        valor,
        round(random.uniform(0, 300), 2),
        fake.cpf()
    ))

conn.commit()

# -----------------------------
# ITENS VENDA
# -----------------------------

print("Inserindo itens de venda...")

for _ in tqdm(range(150000)):

    venda = random.randint(1, 50000)
    produto = random.randint(1, 5000)

    quantidade = random.randint(1, 5)

    valor_unitario = round(random.uniform(10, 3000), 2)

    valor_total = quantidade * valor_unitario

    cursor.execute("""
        INSERT INTO itens_venda
        (
            id_venda,
            id_produto,
            quantidade,
            valor_unitario,
            valor_total
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        venda,
        produto,
        quantidade,
        valor_unitario,
        valor_total
    ))

conn.commit()

# -----------------------------
# USUÁRIOS SISTEMA
# -----------------------------

for i in range(1, 501):

    cursor.execute("""
        INSERT INTO usuarios_sistema
        (
            id_funcionario,
            login,
            senha_hash,
            perfil_acesso
        )
        VALUES (%s,%s,%s,%s)
    """, (
        i,
        fake.unique.user_name(),
        fake.sha256(),
        random.choice([
            'ADMIN',
            'GERENTE',
            'OPERADOR'
        ])
    ))

conn.commit()

# -----------------------------
# LOGS
# -----------------------------

print("Inserindo logs...")

acoes = [
    'LOGIN',
    'LOGOUT',
    'ALTERAÇÃO',
    'EXCLUSÃO',
    'CONSULTA',
    'EXPORTAÇÃO'
]

for _ in tqdm(range(100000)):

    cursor.execute("""
        INSERT INTO logs_acesso
        (
            id_usuario,
            ip_origem,
            navegador,
            sistema_operacional,
            acao_realizada
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        random.randint(1, 500),
        fake.ipv4(),
        fake.chrome(),
        random.choice([
            'Windows',
            'Linux',
            'MacOS'
        ]),
        random.choice(acoes)
    ))

conn.commit()

print("FINALIZADO!")

cursor.close()
conn.close()
