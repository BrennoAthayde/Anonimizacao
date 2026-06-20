import mysql.connector
import time

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "C0rpDBTcc@"

campos_sensiveis = {
    "clientes": {
        "nome_completo": "identificador_direto",
        "cpf": "identificador_direto",
        "rg": "identificador_direto",
        "email": "contato",
        "telefone": "contato",
        "data_nascimento": "quase_identificador_data",
        "renda_mensal": "numerico_sensivel"
    },
    "enderecos_clientes": {
        "cep": "quase_identificador_cep",
        "logradouro": "endereco",
        "numero": "endereco",
        "complemento": "endereco",
        "bairro": "endereco"
    },
    "funcionarios": {
        "nome_completo": "identificador_direto",
        "cpf": "identificador_direto",
        "rg": "identificador_direto",
        "email_corporativo": "contato",
        "telefone": "contato",
        "salario": "numerico_sensivel",
        "data_nascimento": "quase_identificador_data"
    },
    "fornecedores": {
        "cnpj": "identificador_direto",
        "email": "contato",
        "telefone": "contato",
        "cep": "quase_identificador_cep"
    },
    "usuarios_sistema": {
        "login": "identificador_direto",
        "senha_hash": "critico"
    },
    "vendas": {
        "cpf_na_nota": "identificador_direto"
    },
    "pagamentos_venda": {
        "ultimos_digitos_cartao": "critico",
        "codigo_autorizacao": "critico"
    },
    "contratos_crediario": {
        "renda_informada": "numerico_sensivel",
        "score_credito": "numerico_sensivel"
    },
    "entregas": {
        "nome_recebedor": "identificador_direto",
        "cpf_recebedor": "identificador_direto",
        "telefone_recebedor": "contato",
        "cep_entrega": "quase_identificador_cep",
        "endereco_entrega": "endereco"
    },
    "notas_fiscais": {
        "cpf_cnpj_destinatario": "identificador_direto",
        "nome_destinatario": "identificador_direto",
        "chave_acesso": "critico"
    },
    "logs_acesso": {
        "ip_origem": "tecnico",
        "navegador": "tecnico",
        "sistema_operacional": "tecnico"
    }
}


def conectar(database=None):
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database
    )


def coluna_existe(cursor, database, tabela, coluna):
    sql = """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """
    cursor.execute(sql, (database, tabela, coluna))
    return cursor.fetchone()[0] > 0


def tipo_coluna(cursor, database, tabela, coluna):
    sql = """
        SELECT DATA_TYPE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """
    cursor.execute(sql, (database, tabela, coluna))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def remover_unique_se_existir(cursor, database, tabela, coluna):
    sql = """
        SELECT DISTINCT INDEX_NAME
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
          AND NON_UNIQUE = 0
          AND INDEX_NAME != 'PRIMARY'
    """
    cursor.execute(sql, (database, tabela, coluna))
    indices = cursor.fetchall()

    for indice in indices:
        nome_indice = indice[0]
        print(f"   > Removendo UNIQUE: {nome_indice}")
        cursor.execute(f"ALTER TABLE `{tabela}` DROP INDEX `{nome_indice}`")


def valor_mascarado(classificacao, tipo_sql):
    if tipo_sql in ["int", "decimal", "float", "double"]:
        return 0

    if tipo_sql in ["date", "datetime", "timestamp"]:
        return "1900-01-01"

    return "MASCARADO"


def aplicar_mascaramento(cursor, database, tabela, coluna, classificacao):
    if not coluna_existe(cursor, database, tabela, coluna):
        print("   > Ignorado: coluna não existe")
        return 0

    remover_unique_se_existir(cursor, database, tabela, coluna)

    # Mascarar apenas CPF, RG, telefone, CNPJ, cartão e CPF/CNPJ fiscal.
    # Nome, e-mail, endereço, salário, renda e datas serão ignorados no mascaramento.

    if coluna in ["cpf", "cpf_na_nota", "cpf_recebedor"]:
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = CONCAT('***.', SUBSTRING(`{coluna}`, 5, 3), '.', SUBSTRING(`{coluna}`, 9, 3), '-', RIGHT(`{coluna}`, 2))
            WHERE `{coluna}` IS NOT NULL
        """

    elif coluna == "cpf_cnpj_destinatario":
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = 
                CASE
                    WHEN LENGTH(`{coluna}`) <= 14 THEN CONCAT('***.', SUBSTRING(`{coluna}`, 5, 3), '.', SUBSTRING(`{coluna}`, 9, 3), '-', RIGHT(`{coluna}`, 2))
                    ELSE CONCAT('**.', SUBSTRING(`{coluna}`, 4, 3), '.', SUBSTRING(`{coluna}`, 8, 3), '/****-', RIGHT(`{coluna}`, 2))
                END
            WHERE `{coluna}` IS NOT NULL
        """

    elif coluna == "rg":
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = CONCAT('**.***.', RIGHT(`{coluna}`, 3))
            WHERE `{coluna}` IS NOT NULL
        """

    elif coluna in ["telefone", "telefone_recebedor"]:
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = CONCAT('(**) *****-', RIGHT(`{coluna}`, 4))
            WHERE `{coluna}` IS NOT NULL
        """

    elif coluna == "cnpj":
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = CONCAT('**.', SUBSTRING(`{coluna}`, 4, 3), '.', SUBSTRING(`{coluna}`, 8, 3), '/****-', RIGHT(`{coluna}`, 2))
            WHERE `{coluna}` IS NOT NULL
        """

    elif coluna == "ultimos_digitos_cartao":
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = '****'
            WHERE `{coluna}` IS NOT NULL
        """

    else:
        print(f"   > Ignorado: mascaramento não aplicado em {tabela}.{coluna}")
        return 0

    cursor.execute(sql)
    return cursor.rowcount

def aplicar_supressao(cursor, database, tabela, coluna, classificacao):
    if not coluna_existe(cursor, database, tabela, coluna):
        print("   > Ignorado: coluna não existe")
        return 0

    if classificacao not in ["identificador_direto", "critico"]:
        print(f"   > Ignorado: supressão estrutural não recomendada para {classificacao}")
        return 0

    remover_unique_se_existir(cursor, database, tabela, coluna)

    print(f"   > Removendo coluna: {tabela}.{coluna}")
    cursor.execute(f"ALTER TABLE `{tabela}` DROP COLUMN `{coluna}`")

    return 1


def aplicar_generalizacao(cursor, database, tabela, coluna, classificacao):
    if not coluna_existe(cursor, database, tabela, coluna):
        print("   > Ignorado: coluna não existe")
        return 0

    if classificacao == "quase_identificador_data":

        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = STR_TO_DATE(
                CONCAT(YEAR(`{coluna}`), '-01-01'),
                '%Y-%m-%d'
            )
            WHERE `{coluna}` IS NOT NULL
        """

    elif classificacao == "quase_identificador_cep":

        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = CONCAT(
                LEFT(`{coluna}`, 5),
                '-***'
            )
            WHERE `{coluna}` IS NOT NULL
        """

    elif classificacao == "endereco":

        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` =
                TRIM(
                    SUBSTRING_INDEX(`{coluna}`, ',', 1)
                )
            WHERE `{coluna}` IS NOT NULL
        """

    elif classificacao == "numerico_sensivel":

        try:
            cursor.execute(f"""
                ALTER TABLE `{tabela}`
                MODIFY `{coluna}` VARCHAR(30)
            """)
        except:
            pass

        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` =
                CASE

                    WHEN CAST(`{coluna}` AS DECIMAL(15,2)) < 2000
                        THEN '0-2000'

                    WHEN CAST(`{coluna}` AS DECIMAL(15,2)) < 5000
                        THEN '2000-5000'

                    WHEN CAST(`{coluna}` AS DECIMAL(15,2)) < 10000
                        THEN '5000-10000'

                    WHEN CAST(`{coluna}` AS DECIMAL(15,2)) < 20000
                        THEN '10000-20000'

                    ELSE '20000+'

                END
            WHERE `{coluna}` IS NOT NULL
        """

    else:
        print(f"   > Ignorado: generalização não recomendada para {classificacao}")
        return 0

    cursor.execute(sql)
    return cursor.rowcount


def aplicar_ruido(cursor, database, tabela, coluna, classificacao):
    if not coluna_existe(cursor, database, tabela, coluna):
        print("   > Ignorado: coluna não existe")
        return 0

    if classificacao != "numerico_sensivel":
        print("   > Ignorado: ruído só será aplicado em campos numéricos sensíveis")
        return 0

    sql_type = tipo_coluna(cursor, database, tabela, coluna)

    if sql_type not in ["int", "decimal", "float", "double"]:
        print(f"   > Ignorado: {tabela}.{coluna} não é campo numérico")
        return 0

    if coluna == "score_credito":
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = GREATEST(
                0,
                LEAST(
                    1000,
                    `{coluna}` + FLOOR(RAND() * 101) - 50
                )
            )
            WHERE `{coluna}` IS NOT NULL
        """
    else:
        sql = f"""
            UPDATE `{tabela}`
            SET `{coluna}` = ROUND(
                `{coluna}` * (1 + ((RAND() * 0.20) - 0.10)),
                2
            )
            WHERE `{coluna}` IS NOT NULL
        """

    cursor.execute(sql)
    return cursor.rowcount


def aplicar_permutacao(cursor, database, tabela, coluna, classificacao):
    import random

    colunas_permutaveis = [
        "cpf",
        "rg",
        "cpf_na_nota",
        "cpf_recebedor",
        "cpf_cnpj_destinatario",
        "renda_mensal",
        "salario",
        "renda_informada",
        "score_credito"
    ]

    if coluna not in colunas_permutaveis:
        print(f"   > Ignorado: {tabela}.{coluna} não é adequado para permutação")
        return 0

    if not coluna_existe(cursor, database, tabela, coluna):
        print("   > Ignorado: coluna não existe")
        return 0

    remover_unique_se_existir(cursor, database, tabela, coluna)


    sql_pk = """
        SELECT COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = %s
        AND CONSTRAINT_NAME = 'PRIMARY'
        LIMIT 1
    """

    cursor.execute(sql_pk, (database, tabela))
    resultado = cursor.fetchone()

    if not resultado:
        print("   > Ignorado: tabela sem chave primária")
        return 0

    chave_primaria = resultado[0]

    cursor.execute(f"""
        SELECT `{chave_primaria}`, `{coluna}`
        FROM `{tabela}`
        WHERE `{coluna}` IS NOT NULL
    """)

    registros = cursor.fetchall()

    if len(registros) < 2:
        print("   > Poucos registros para permutação")
        return 0

    ids = [r[0] for r in registros]
    valores = [r[1] for r in registros]

    valores_embaralhados = valores.copy()

    tentativas = 0
    while valores_embaralhados == valores and tentativas < 10:
        random.shuffle(valores_embaralhados)
        tentativas += 1

    afetados = 0

    for id_registro, novo_valor in zip(ids, valores_embaralhados):
        cursor.execute(
            f"""
            UPDATE `{tabela}`
            SET `{coluna}` = %s
            WHERE `{chave_primaria}` = %s
            """,
            (novo_valor, id_registro)
        )

        afetados += cursor.rowcount

    return afetados


def aplicar_tecnica(database, tecnica, tabelas_escolhidas):
    conn = conectar(database)
    cursor = conn.cursor()

    inicio = time.time()
    total_afetado = 0

    for tabela in tabelas_escolhidas:
        if tabela not in campos_sensiveis:
            print(f"Tabela {tabela} não possui campos sensíveis mapeados. Ignorando.")
            continue

        print(f"\nAplicando técnica na tabela: {tabela}")

        for coluna, classificacao in campos_sensiveis[tabela].items():
            print(f" - Campo: {coluna} ({classificacao})")

            if tecnica == "1":
                afetados = aplicar_mascaramento(cursor, database, tabela, coluna, classificacao)

            elif tecnica == "2":
                afetados = aplicar_supressao(cursor, database, tabela, coluna, classificacao)

            elif tecnica == "3":
                afetados = aplicar_generalizacao(cursor, database, tabela, coluna, classificacao)

            elif tecnica == "4":
                afetados = aplicar_ruido(cursor, database, tabela, coluna, classificacao)

            elif tecnica == "5":
                afetados = aplicar_permutacao(cursor, database, tabela, coluna, classificacao)

            else:
                print("Técnica inválida.")
                afetados = 0

            total_afetado += afetados
            print(f"   > Registros/colunas afetados: {afetados}")

    conn.commit()

    fim = time.time()
    tempo_total = round(fim - inicio, 2)

    cursor.close()
    conn.close()

    print("\n====================================")
    print("Técnica aplicada com sucesso.")
    print(f"Total de registros/colunas afetados: {total_afetado}")
    print(f"Tempo total: {tempo_total} segundos")
    print("====================================")


def main():
    print("====================================")
    print(" SISTEMA DE ANONIMIZAÇÃO - TCC")
    print("====================================")

    database = input("Digite o nome do banco de dados: ").strip()

    print("\nEscolha a técnica:")
    print("1 - Mascaramento")
    print("2 - Supressão estrutural (DROP COLUMN)")
    print("3 - Generalização")
    print("4 - Adição de ruído")
    print("5 - Permutação")

    tecnica = input("Opção: ").strip()

    print("\nDeseja aplicar em:")
    print("1 - Todo o banco mapeado")
    print("2 - Tabelas específicas")

    escopo = input("Opção: ").strip()

    if escopo == "1":
        tabelas_escolhidas = list(campos_sensiveis.keys())
    else:
        print("\nTabelas disponíveis:")
        for tabela in campos_sensiveis.keys():
            print(f"- {tabela}")

        entrada = input("\nDigite as tabelas separadas por vírgula: ")
        tabelas_escolhidas = [t.strip() for t in entrada.split(",")]

    print("\nATENÇÃO: essa ação irá alterar a estrutura/dados do banco.")
    print("Para supressão, colunas serão removidas definitivamente.")
    confirmar = input("Deseja continuar? (s/n): ").strip().lower()

    if confirmar != "s":
        print("Operação cancelada.")
        return

    aplicar_tecnica(database, tecnica, tabelas_escolhidas)


if __name__ == "__main__":
    main()
