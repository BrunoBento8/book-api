# Correção: Banco de Dados Vazio no Render

## Problema

A API no Render retorna dados vazios:
```json
{
  "books": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 0
}
```

## Causa

O banco de dados SQLite foi criado durante o deploy, mas os dados do CSV não foram importados. Isso pode acontecer se:
1. O script `init_database.py` encontrou algum erro durante a importação
2. O CSV existe mas a importação foi pulada por já existir um banco vazio
3. Permissões ou timeout durante o build

## Solução 1: Usar o Novo Endpoint de Importação (RECOMENDADO)

Criei um novo endpoint administrativo que força a importação do CSV existente.

### Passo 1: Fazer Deploy do Código Atualizado

```bash
cd /Users/nsx001191/Documents/fiap/book-api
git add .
git commit -m "Add force CSV import endpoint for Render"
git push origin feat-adding-api
```

O Render vai fazer o deploy automaticamente.

### Passo 2: Fazer Login como Admin

Obtenha o token de acesso do admin:

```bash
# Substitua pela URL do seu app no Render
curl -X POST "https://seu-app.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "sua_senha_admin"
  }'
```

Copie o `access_token` da resposta.

### Passo 3: Forçar Importação do CSV

```bash
# Substitua YOUR_TOKEN e a URL
curl -X POST "https://seu-app.onrender.com/api/v1/scraping/import-csv" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Se o banco já tiver dados (mesmo que vazios), use `force=true`:

```bash
curl -X POST "https://seu-app.onrender.com/api/v1/scraping/import-csv?force=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Passo 4: Verificar os Dados

```bash
curl "https://seu-app.onrender.com/api/v1/books"
```

Deve retornar os livros com sucesso!

## Solução 2: Executar Script Manual via Shell (Alternativa)

Se a Solução 1 não funcionar, você pode acessar o Shell do Render:

### Passo 1: Acessar o Dashboard do Render

1. Vá para https://dashboard.render.com
2. Selecione seu serviço
3. Clique em "Shell" no menu lateral

### Passo 2: Executar o Script de Migração

```bash
python scripts/migrate_csv_to_db.py
```

Ou use o script de inicialização:

```bash
python scripts/init_database.py
```

## Solução 3: Modificar o Build Command

Se você quer garantir que os dados sejam importados em todo deploy:

### Atualizar render.yaml

Edite o arquivo `render.yaml` e modifique o `buildCommand`:

```yaml
buildCommand: |
  pip install -r requirements.txt
  mkdir -p data
  python scripts/init_database.py
  python scripts/migrate_csv_to_db.py || echo "Migration skipped or already complete"
```

Depois faça commit e push:

```bash
git add render.yaml
git commit -m "Force CSV import on every build"
git push origin feat-adding-api
```

## Verificação de Sucesso

Após executar qualquer solução, verifique:

### 1. Endpoint de Livros
```bash
curl "https://seu-app.onrender.com/api/v1/books" | jq
```

Deve retornar `total > 0` e uma lista de livros.

### 2. Endpoint de Estatísticas
```bash
curl "https://seu-app.onrender.com/api/v1/stats/overview" | jq
```

Deve mostrar estatísticas dos livros.

### 3. Endpoint de Categorias
```bash
curl "https://seu-app.onrender.com/api/v1/categories" | jq
```

Deve listar as categorias disponíveis.

## Logs para Diagnóstico

Para ver os logs do Render e identificar o problema:

1. Vá para o Dashboard do Render
2. Selecione seu serviço
3. Clique em "Logs"
4. Procure por:
   - `✅ X livros importados com sucesso` (sucesso)
   - `⚠️ Arquivo CSV não encontrado` (CSV ausente)
   - `❌ Erro ao importar livros` (erro na importação)
   - `⚠️ Banco já contém X livros` (pular importação)

## Prevenção Futura

Para evitar esse problema em futuros deploys:

1. **Sempre verifique os logs após o deploy**
2. **Teste o endpoint `/api/v1/books` imediatamente**
3. **Configure o ADMIN_PASSWORD nas variáveis de ambiente**
4. **Use o endpoint de health check para monitoramento**

## Novo Endpoint Criado

### POST /api/v1/scraping/import-csv

**Parâmetros:**
- `force` (opcional, boolean): Se `true`, deleta todos os livros e reimporta

**Autenticação:**
- Requer token de admin no header: `Authorization: Bearer {token}`

**Respostas:**

**Sucesso (200):**
```json
{
  "status": "success",
  "message": "Successfully imported 1000 books from CSV",
  "imported": 1000,
  "csv_books": 1000,
  "triggered_by": "admin"
}
```

**Banco já populado (200):**
```json
{
  "status": "skipped",
  "message": "Database already contains 1000 books",
  "csv_books": 1000,
  "note": "Use force=true parameter to delete and reimport all books"
}
```

**CSV não encontrado (400):**
```json
{
  "detail": "CSV file not found at /path/to/books.csv. Please run the scraper first."
}
```

**Sem autorização (403):**
```json
{
  "detail": "Admin privileges required"
}
```

## Testando Localmente

Antes de fazer deploy, teste localmente:

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar API
uvicorn app.main:app --reload

# Em outro terminal, testar o endpoint
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Usar o token para importar
curl -X POST "http://localhost:8000/api/v1/scraping/import-csv" \
  -H "Authorization: Bearer SEU_TOKEN"

# Verificar livros
curl "http://localhost:8000/api/v1/books"
```

## Suporte

Se nenhuma solução funcionar:
1. Verifique os logs completos do Render
2. Confirme que o arquivo `data/books.csv` existe no repositório Git
3. Verifique as permissões do disco no Render
4. Verifique se o ADMIN_PASSWORD está configurado nas variáveis de ambiente
