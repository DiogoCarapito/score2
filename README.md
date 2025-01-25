# python_project_template

[![Github Actions Workflow](https://github.com/DiogoCarapito/score2/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/score2/actions/workflows/main.yaml)

SCORE2 Algorithm. includes SCORE2-OP and SCORE2-DM

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
