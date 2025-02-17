# python_project_template

[![Github Actions Workflow](https://github.com/DiogoCarapito/score2/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/score2/actions/workflows/main.yaml)

Calculadora de SCORE2, SCORE2-OP and SCORE2-DM com base em dados do MIM@UF.

Permite calcular o Risco Cardiovascular de uma unidade toda a quem tem a informação registada nos relatórios do MIM@UF

- **P01.01.L01 - Inscritos** Lista de utentes que se pretende selecionar (unidade inteira ou apenas uma lista de um médico de família, por exemplo). Esta lista tem o NUtente, Médico de Familia, sexo e idade com data de nascimento (útil para calcular idades fora da extração)

- **P04.01.L01 - Problemas** para ter a lista de diagnósticos relevantes para o cálculo, nomeadamente tabagismo (P17), Diabetes (T90 e T89), doença cardiovascular establecida (K74, K75, K76, K98, K90, K91, K92). Podem ser extraidos todos de uma vez executando o a seleção de ICPCs com todos separados de virgula antes da execução do relatório: P17, T90, T89, K74, K75, K76, K98, K90, K91, K92. De forma a que todos os diagnósticos estejam numa unica folha, há que passar o filtro ICPC para coluna, antes de exportar o relatório.

- **P07.03.L01 - Resultados de MCDTs** é a forma de extrair o último valor do Colesterol total, HDL, Triglicéridos, LDL (que pode ser doseado à parte ou calculado com o perfil lipidico, utiliza-se o que for mais recente), creatinina, albuminúria e Hemoglobina A1c. Têm que ser estraidos um de cada vez =/

- **P010.01.L01 - Biometrias** para ter o último valor de Tensão arterial sistólica (TAs) e a data do diagnóstico da diabetes (DM desde)

As tabelas são todas juntas e o valor do SCORE 2 e a sua interpretação, tanto o risco como a adeuqação do valor do LDL (alvo ou acima do alvo) são calculados se os dados necessários estiverem presentes.

É escolhido qual SCORE se aplica consoante as regras:

- SCORE2: >=40 a <70, sem DM
- SCORE2-OP >=70 anos
- SCORE2-DM >=40 a <70, com DM

Utentes com doença cardiovascular establecida (DCV) automaticamente são classificadas como muito alto risco e o SCORE não é calculado:

- K74, K75, K76: Doença coronária
- K89, K90, K91, K92: Doença cerebrovascular

Os alvos de LDL escolhidos são consoante o risco calculado e o valor de LDL:

- Baixo: <116 mg/dL
- Moderado: <100 mg/dL
- Baixo a Moderado: <100 mg/dL
- Alto: <70 mg/dL
- Muito alto: <55 mg/dL
- DCV: <55 mg/dL


## Como utilizar?

Esta app está desenhada como uma aplicação de internet (webapp) mas deve ser usada no computador local (sem internet), uma vez para o seu funcionamento desejado inclui dados pessoais e sensíveis de utentes, pelo que correr com base na internet náo é opção neste momento.

1 - Abrir programa de desenvolvimento à escolha (Ex. Visual Studio Code)

2 - Abrir novo projeto a partir de clone de repositório: *https://github.com/DiogoCarapito/score2* OU no abrir um projeto novo e executar no terminal

```bash
git clone https://github.com/DiogoCarapito/score2
```

3 - No termina, instalar uma versão de python local em ambiente virtual

```bash
python3.12 -m venv .venv
```

4 - Activar o ambiente virtual

```bash
source .venv/bin/activate
```

5 - Instalar as bibliotecas necessárias

```bash
make install
```

6 - Iniciar a aplicação que irá abrir no browser automaticamente (se não iniciar estará em URL local tipo *http://localhost:8501*)

```bash
streamlit run SCORE2.py
```

7 - Fazer upload dos ficheiros .xlsx vindos do MIM@UF (mas têm de ser abertos no excel primeiro e gravados em formato de livro). podem ser colocados todos ao mesmo tempo!

8 - O processamento dos ficheiros incicia quando todos estiverem presentes e corretos. irá aparecer a tabela final com toda a informação junta e o SCORE 2 calculado

---

## cheat sheet

### setup

move all files and folders to the current project folder

```bash
mv python_project_template/{*,.*} . && rm -r python_project_template/
```

### venv

create venv

```bash
python3.12 -m venv .venv
```

activate venv

```bash
source .venv/bin/activate
```

### Docker

build docker image

```bash
docker build -t main:latest .
```
