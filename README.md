# Portal de Atos do Diário Oficial da União (DOU)

Aplicação web completa para consulta e monitoramento de atos oficiais publicados no Diário Oficial da União - Seção 2 (Atos de Pessoal).

## 🚀 Funcionalidades

- **Consulta por Órgão**: Selecione entre múltiplos órgãos da administração pública federal
- **Filtros Avançados**: Busque por nome, cargo, tipo de ato ou termo livre
- **Visualização Organizada**: Interface limpa com badges coloridos por tipo de ato
- **API REST**: Backend completo com FastAPI para integração
- **Dados em Tempo Real**: Coleta e atualização automática de dados do DOU

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação e Uso Local

### Opção 1: Usando o script automático (Recomendado)

```bash
# No Linux/Mac
./rodarotina.sh

# No Windows (Git Bash ou WSL)
bash rodarotina.sh
```

### Opção 2: Manual

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Inicie o servidor
python server.py
```

### Acessando a Aplicação

Após iniciar o servidor, acesse:

- **Interface Web**: http://127.0.0.1:8000
- **Documentação da API**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 🌐 Deploy Online (Gratuito)

### Opção 1: Render.com

1. Crie uma conta em [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Clique em "Create Web Service"

### Opção 2: Railway.app

1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Selecione este repositório
4. Adicione variável de ambiente: `PORT=8000`
5. Railway detectará automaticamente o Python e instalará dependências

### Opção 3: Vercel

1. Instale a CLI: `npm i -g vercel`
2. Crie um arquivo `vercel.json`:
```json
{
  "builds": [{ "src": "server.py", "use": "@vercel/python" }]
}
```
3. Execute: `vercel deploy`

### Opção 4: Hugging Face Spaces

1. Crie um Space em [huggingface.co/spaces](https://huggingface.co/spaces)
2. Escolha "Docker" como SDK
3. Faça upload dos arquivos
4. O Space será deployed automaticamente

## 📁 Estrutura do Projeto

```
/workspace
├── server.py           # Backend FastAPI (servidor principal)
├── index.html          # Frontend (interface web)
├── requirements.txt    # Dependências Python
├── rodarotina.sh       # Script de inicialização
├── README.md           # Este arquivo
└── dados_dou_orgaos.json  # Banco de dados JSON (gerado automaticamente)
```

## 🔌 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Serve a interface web |
| `/api/organizacoes` | GET | Lista todos os órgãos disponíveis |
| `/api/atos` | GET | Lista atos com filtros (orgao, q, tipo) |
| `/api/coletar` | GET | Força coleta de novos dados |
| `/health` | GET | Verifica saúde da API |
| `/docs` | GET | Documentação Swagger UI |

### Exemplos de Uso da API

```bash
# Listar todos os órgãos
curl http://localhost:8000/api/organizacoes

# Listar atos do IPEA
curl "http://localhost:8000/api/atos?orgao=IPEA"

# Buscar atos com termo específico
curl "http://localhost:8000/api/atos?orgao=TODOS&q=nomeacao"

# Filtrar por tipo
curl "http://localhost:8000/api/atos?orgao=MEC&tipo=Exoneração"

# Forçar coleta de dados
curl "http://localhost:8000/api/coletar?orgao=TODOS"
```

## 🛠️ Personalização

### Adicionar Novos Órgãos

Edite o arquivo `server.py` e adicione na lista `ORGANIZACOES`:

```python
ORGANIZACOES = [
    # ... órgãos existentes ...
    {"sigla": "NOVO", "nome": "Nome do Novo Órgão"},
]
```

### Implementar Scraping Real

Atualmente a aplicação usa dados simulados. Para implementar scraping real do DOU:

1. Modifique a função `coletar_atos()` em `server.py`
2. Use bibliotecas como `requests` + `BeautifulSoup` ou `Selenium`
3. Parseie o HTML do site [in.gov.br](https://www.in.gov.br)

## 📝 Licença

Este projeto é open source e pode ser usado livremente para fins educacionais e governamentais.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

---

**Desenvolvido para facilitar o acesso e transparência dos atos oficiais da Administração Pública Federal.**