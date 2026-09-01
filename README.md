# Portal de Atos do Diário Oficial da União (DOU)

Aplicação web completa para consulta e monitoramento de atos oficiais publicados no Diário Oficial da União - Seção 2 (Atos de Pessoal), com integração real à API do **Ro-dou** (gestão.gov.br).

## 🚀 Funcionalidades

- **Dados Reais do DOU**: Integração com a API pública do Ro-dou para buscar atos oficiais automaticamente
- **Consulta por Órgão**: Selecione entre múltiplos órgãos da administração pública federal
- **Filtros Avançados**: Busque por nome, cargo, tipo de ato, período ou termo livre
- **Resumo Dinâmico**: Painel estatístico no topo com totais calculados em tempo real (Movimentações, FCE, Nomeações, Exonerações, etc.)
- **Tabela Estruturada**: Visualização detalhada com colunas: Nome, Cargo, Sigla, FCE, Tipo de Ato, Diretoria, Portaria, Data, Vigência e Link
- **API REST**: Backend completo com FastAPI para integração
- **Links Funcionais**: Acesso direto à íntegra dos atos no site oficial do DOU
- **Deploy Fácil**: Pronto para rodar localmente, em Docker ou na nuvem (Render, Railway, etc.)

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Conexão com internet (para buscar dados reais do DOU)

## 🔧 Instalação e Uso Local

### Opção 1: Usando o script automático (Recomendado)

```bash
# No Linux/Mac
chmod +x rodarotina.sh
./rodarotina.sh

# No Windows (Git Bash ou WSL)
bash rodarotina.sh
```

### Opção 2: Manual

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Inicie o servidor
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Opção 3: Docker

```bash
# Build da imagem
docker build -t portal-dou .

# Rodar container
docker run -p 8000:8000 portal-dou
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
   - **Start Command**: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Docker**: Use o Dockerfile incluído (opcional)
5. Clique em "Create Web Service"

⚠️ **Nota:** No plano gratuito, o serviço "dorme" após 15 minutos de inatividade.

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
├── server.py              # Backend FastAPI (servidor principal + schemas)
├── index.html             # Frontend (interface web com resumo e tabela)
├── dou_search.py          # Motor de coleta (integração API Ro-dou)
├── parser_dou.py          # Parser de dados brutos para estrutura padronizada
├── requirements.txt       # Dependências Python
├── rodarotina.sh          # Script de inicialização
├── Dockerfile             # Docker para desenvolvimento
├── Dockerfile.prod        # Docker para produção
├── README.md              # Este arquivo
└── dados_dou_orgaos.json  # Banco de dados JSON (cache local)
```

## 🔌 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Serve a interface web |
| `/api/organizacoes` | GET | Lista todos os órgãos disponíveis |
| `/api/atos` | GET | Lista atos (prioriza cache real, fallback para simulado) |
| `/api/buscar_real` | GET | **Busca dados reais no DOU via API Ro-dou** |
| `/api/coletar` | GET | Força coleta/atualização de dados |
| `/health` | GET | Verifica saúde da API |
| `/docs` | GET | Documentação Swagger UI |

### Exemplos de Uso da API

```bash
# Listar todos os órgãos
curl http://localhost:8000/api/organizacoes

# Listar atos (do cache ou simulados)
curl "http://localhost:8000/api/atos?orgao=IPEA"

# **Buscar dados REAIS no DOU (integração Ro-dou)**
curl "http://localhost:8000/api/buscar_real?orgao=IPEA&dias=7"

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

### Configurar Busca no Ro-dou

O sistema já vem configurado para usar a API pública do Ro-dou. Para personalizar parâmetros de busca:

1. Edite `dou_search.py` para ajustar termos padrão ou filtros
2. Modifique `parser_dou.py` para refinar a extração de campos específicos (nome, cargo, FCE, etc.)

## 📊 Como Funciona o Fluxo de Dados

1. **Usuário clica em "🔍 Buscar no DOU Real"** no frontend
2. **Frontend chama** `/api/buscar_real` no backend
3. **Backend (`dou_search.py`)** consulta a API do Ro-dou com os filtros selecionados
4. **Parser (`parser_dou.py`)** processa os dados brutos, extraindo:
   - Nome do servidor
   - Cargo/Função
   - Código FCE/DAS
   - Tipo de ato (Nomeação, Exoneração, Substituição, etc.)
   - Vigência e outras informações estruturadas
5. **Cache Global** armazena os dados processados
6. **Frontend atualiza**:
   - Painel de Resumo (cálculos automáticos)
   - Tabela Estruturada (linhas preenchidas)
   - Links funcionais para o DOU oficial

## 📝 Licença

Este projeto é open source e pode ser usado livremente para fins educacionais e governamentais.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

---

**Desenvolvido para facilitar o acesso e transparência dos atos oficiais da Administração Pública Federal.**

*Integração com dados reais fornecida pela API do [Ro-dou](https://github.com/gestaogovbr/Ro-dou).*