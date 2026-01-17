# 📊 Dashboard de Monitoramento - Guia de Configuração

## Problema Resolvido

O dashboard Streamlit estava apresentando erro de validação do Pydantic porque as variáveis de ambiente não eram carregadas antes da importação das configurações.

### Erro Original:
```
ValidationError: 5 validation errors for Settings
APP_NAME Field required
APP_VERSION Field required
ENVIRONMENT Field required
DATABASE_URL Field required
SECRET_KEY Field required
```

## Solução Implementada

### 1. Carregamento Explícito do .env

Modificado o arquivo `monitoring/dashboard.py` para carregar as variáveis de ambiente ANTES de importar as configurações:

```python
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables BEFORE importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.config import settings
```

### 2. Dependências Atualizadas

Adicionadas as bibliotecas necessárias ao `requirements.txt`:
- `streamlit==1.40.2` - Framework do dashboard
- `plotly==5.24.1` - Visualizações interativas

### 3. Script de Inicialização

Criado o script `run_dashboard.sh` para facilitar a execução:

```bash
#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting Book API Monitoring Dashboard..."
streamlit run monitoring/dashboard.py
```

Tornar executável com: `chmod +x run_dashboard.sh`

## Como Usar

### Opção 1: Script de Inicialização (Recomendado)
```bash
./run_dashboard.sh
```

### Opção 2: Comando Direto
```bash
streamlit run monitoring/dashboard.py
```

### Opção 3: Com Parâmetros Personalizados
```bash
streamlit run monitoring/dashboard.py --server.port 8502 --server.headless true
```

## Acesso

Após inicializar, o dashboard estará disponível em:
- **URL Local**: http://localhost:8501
- **URL Rede**: http://<seu-ip>:8501 (se configurado)

## Recursos do Dashboard

### KPIs Principais
- 📈 Total de Requisições (com delta da última hora)
- ⚡ Tempo Médio de Resposta (com P95)
- ⚠️ Taxa de Erro (porcentagem de 4xx/5xx)
- 📚 Total de Livros e Categorias

### Visualizações
1. **Requisições ao Longo do Tempo** - Linha temporal com agregação horária
2. **Top 10 Endpoints** - Barras horizontais dos mais acessados
3. **Distribuição de Tempo de Resposta** - Histograma de performance
4. **Códigos HTTP** - Pizza com distribuição de status
5. **Requisições Recentes** - Tabela das últimas 20 com cores

### Filtros de Tempo
- Última Hora
- Últimas 6 Horas
- Últimas 24 Horas
- Últimos 7 Dias
- Todo o Período

### Funcionalidades
- 🔄 Auto-refresh a cada 30 segundos
- 🎨 Coloração automática de status codes
- 📊 Métricas em tempo real
- 📱 Layout responsivo

## Requisitos de Sistema

- Python 3.10+
- Arquivo `.env` configurado corretamente
- Banco de dados SQLite com tabelas `api_logs` e `books`
- API rodando e gerando logs

## Verificação de Funcionamento

### 1. Testar Carregamento de Configurações
```bash
python3 -c "from dotenv import load_dotenv; load_dotenv(); from app.config import settings; print('✅ Settings OK:', settings.APP_NAME)"
```

### 2. Verificar Banco de Dados
```bash
sqlite3 data/books.db "SELECT COUNT(*) FROM api_logs;"
```

### 3. Iniciar Dashboard
```bash
streamlit run monitoring/dashboard.py
```

## Troubleshooting

### Erro: "streamlit: command not found"
```bash
pip install streamlit==1.40.2
```

### Erro: "No module named 'plotly'"
```bash
pip install plotly==5.24.1
```

### Erro: "No such file or directory: .env"
Certifique-se de que o arquivo `.env` existe no diretório raiz do projeto.

### Dashboard vazio / sem dados
- Verifique se a API está rodando
- Faça algumas requisições para gerar logs
- Confirme que a tabela `api_logs` existe no banco

## Integração com a API

O dashboard lê dados da mesma fonte que a API:
- **Banco de Dados**: `data/books.db` (SQLite)
- **Tabelas**: `api_logs`, `books`
- **Configurações**: `.env` compartilhado

Para gerar dados de teste:
```bash
# Inicie a API
uvicorn app.main:app --reload

# Faça requisições
curl http://localhost:8000/api/v1/books
curl http://localhost:8000/api/v1/categories
curl http://localhost:8000/api/v1/stats/overview
```

## Próximos Passos

- [ ] Adicionar métricas de uso de memória
- [ ] Implementar alertas de performance
- [ ] Export de relatórios em PDF
- [ ] Dashboard histórico com comparações
- [ ] Integração com ferramentas de alerta (email, Slack)

## Referências

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- [Python Dotenv](https://github.com/theskumar/python-dotenv)
