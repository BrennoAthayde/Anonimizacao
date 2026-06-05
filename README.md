# Anonimização de Dados Sensíveis em Bancos de Dados Corporativos

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC), com o objetivo de analisar e implementar técnicas de anonimização e mascaramento de dados para adequação à Lei Geral de Proteção de Dados (LGPD).

## Sobre o Projeto

A crescente preocupação com a privacidade e a proteção de dados exige que organizações adotem mecanismos capazes de reduzir a exposição de informações pessoais e sensíveis. Este projeto propõe a implementação e avaliação de diferentes técnicas de anonimização aplicadas a bancos de dados corporativos, permitindo a utilização segura das informações para testes, desenvolvimento e análise de dados.

O ambiente foi desenvolvido utilizando dados sintéticos gerados artificialmente, garantindo que nenhum dado real seja utilizado durante os experimentos.

## Objetivos

* Implementar técnicas de anonimização de dados;
* Avaliar o impacto das técnicas na utilidade das informações;
* Verificar a conformidade com os princípios da LGPD;
* Analisar o desempenho computacional das técnicas aplicadas;
* Identificar riscos de reidentificação dos titulares dos dados.

## Técnicas Implementadas

### Mascaramento

Substitui parcial ou totalmente os dados originais por caracteres ou valores fictícios.

### Supressão

Remove completamente atributos considerados sensíveis ou identificadores.

### Generalização

Reduz o nível de detalhamento das informações, agrupando valores em categorias ou intervalos.

### Adição de Ruído

Insere pequenas alterações nos dados para dificultar a identificação dos indivíduos.

### Permutação

Realiza a troca de valores entre registros mantendo a consistência estrutural do banco.

## Tecnologias Utilizadas

* Python 3.12
* MySQL
* Faker
* Ubuntu Server 24.04
* DBeaver

## Estrutura do Projeto

```text
.
├── populaDB.py
├── anonimizaDB.py
├── README.md

```

## Ambiente de Testes

O ambiente experimental utiliza um banco de dados corporativo fictício denominado "Megastore", composto por tabelas que simulam operações comuns de uma organização, incluindo clientes, funcionários, vendas, produtos e registros de auditoria.

Os dados são gerados automaticamente utilizando a biblioteca Faker, permitindo a criação de grandes volumes de informações para análise das técnicas de anonimização.

## Como Executar

### Clonar o Repositório

```bash
git clone https://github.com/BrennoAthayde/Anonimizacao.git
cd Anonimizacao
```

### Instalar Dependências

```bash
pip install faker mysql-connector-python
```

### Popular o Banco de Dados

```bash
python3 populaDB.py
```

### Executar a Anonimização

```bash
python3 anonimizaDB.py
```

## Resultados Esperados

* Redução da exposição de dados pessoais e sensíveis;
* Preservação da utilidade dos dados para testes e desenvolvimento;
* Apoio à conformidade com a LGPD.

## Autor

Brenno da Silva Athaide Rodrigues

## Licença

Este projeto possui finalidade exclusivamente acadêmica e educacional.
