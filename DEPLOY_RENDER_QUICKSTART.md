# 🚀 Deploy no Render - Guia Rápido

## 📋 Checklist Pré-Deploy

Antes de tudo, confirme:
- ✅ Código está no GitHub
- ✅ Arquivo `data/books.csv` está no repositório
- ✅ Branch `feat-adding-api` está atualizada
- ✅ Conta criada no [Render.com](https://dashboard.render.com)

## 🎯 Passo a Passo para Deploy

### 1️⃣ Conectar Repositório ao Render

1. Acesse https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Conecte sua conta do GitHub (se ainda não conectou)
4. Selecione o repositório `book-api`
5. Clique em **"Connect"**

### 2️⃣ Configurar o Serviço

Na tela de configuração, preencha:

**Configurações Básicas:**
- **Name**: `book-recommendation-api` (ou outro nome)
- **Region**: `Oregon (US West)` (ou mais próximo)
- **Branch**: `feat-adding-api` (ou `main`)
- **Root Directory**: deixe vazio (ou `book-api` se estiver em subpasta)
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt && mkdir -p data && python scripts/init_database.py
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Plan:**
- Selecione **"Free"** (suficiente para o projeto)

### 3️⃣ Configurar Variáveis de Ambiente

Role até a seção **"Environment Variables"** e adicione:

```bash
APP_NAME=book-recommendation-api
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=sqlite:///./data/books.db
SECRET_KEY=sua-chave-super-secreta-mude-isso-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["*"]
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@bookapi.com
ADMIN_PASSWORD=Admin@123
```

**⚠️ IMPORTANTE:**
- Marque `SECRET_KEY` como **Secret** ✅
- Marque `ADMIN_PASSWORD` como **Secret** ✅
- Use uma senha forte em produção!

### 4️⃣ Adicionar Disco Persistente (CRÍTICO!)

**⚠️ MUITO IMPORTANTE - Sem isso você perderá os dados!**

Na seção **"Advanced"**, clique em **"Add Disk"**:

- **Name**: `data-disk`
- **Mount Path**: `/opt/render/project/src/data`
- **Size**: `1 GB` (suficiente)

### 5️⃣ Configurar Health Check

Na seção **"Health Check"**:

- **Health Check Path**: `/api/v1/health`

### 6️⃣ Deploy!

1. Revise todas as configurações
2. Clique em **"Create Web Service"**
3. Aguarde o build e deploy (pode levar 3-5 minutos)

## 🔍 Verificação Pós-Deploy

### 1. Verificar Logs de Build

No Render Dashboard, vá em **"Logs"** e procure:

```
✅ Tabelas criadas: api_logs, books, users
✅ 1000 livros importados com sucesso
✅ Admin criado com sucesso!
✅ INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!
```

Se ver esses logs, está tudo certo! ✅

### 2. Obter URL da API

No topo do dashboard do serviço, você verá:

```
https://book-recommendation-api.onrender.com
```

Copie esta URL! 📋

### 3. Testar Health Check

Abra no navegador ou use curl:

```bash
curl https://SEU-APP.onrender.com/api/v1/health
```

**Resposta esperada:**
```json
{
  "status": "saudável",
  "app_name": "book-recommendation-api",
  "version": "1.0.0",
  "environment": "production",
  "database": "conectado"
}
```

### 4. Testar Autenticação

```bash
curl -X POST "https://SEU-APP.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin@123"
```

**Se retornar tokens, está funcionando!** ✅

### 5. Acessar Swagger Docs

Abra no navegador:

```
https://SEU-APP.onrender.com/docs
```

Você verá a documentação interativa da API! 📚

### 6. Testar Endpoints

```bash
# Listar livros
curl https://SEU-APP.onrender.com/api/v1/books

# Buscar livro
curl https://SEU-APP.onrender.com/api/v1/books/1

# Categorias
curl https://SEU-APP.onrender.com/api/v1/categories

# Estatísticas
curl https://SEU-APP.onrender.com/api/v1/stats/overview
```

## 🎉 Pronto!

Se todos os testes passaram, sua API está **LIVE** em produção! 🚀

**URL da API**: https://SEU-APP.onrender.com
**Swagger Docs**: https://SEU-APP.onrender.com/docs

## 🔧 Usando render.yaml (Alternativa Mais Fácil!)

Se seu repositório já tem o arquivo `render.yaml`, o processo é MUITO mais simples:

### Opção Alternativa: Blueprint Deploy

1. Acesse https://dashboard.render.com
2. Clique em **"New +"** → **"Blueprint"**
3. Selecione seu repositório
4. O Render detecta o `render.yaml` automaticamente
5. **APENAS configure manualmente**:
   - `ADMIN_PASSWORD` (marque como Secret)
6. Clique em **"Apply"**
7. Pronto! ✅

O `render.yaml` já tem todas as configurações corretas!

## ⚠️ Problemas Comuns

### Erro: "no such table: books"

**Solução:**
1. Vá em **"Manual Deploy"** → **"Clear build cache & deploy"**
2. Isso força um rebuild completo
3. Verifique nos logs se o `init_database.py` executou com sucesso

### Erro: Build falhou

**Verifique:**
- O arquivo `requirements.txt` está no root do repositório
- O arquivo `scripts/init_database.py` existe
- O arquivo `data/books.csv` existe no repositório

### API está lenta na primeira requisição

**Normal!** O plano free do Render hiberna após 15 min de inatividade.
- Primeira requisição: 30-60 segundos (acordando)
- Próximas requisições: rápidas

### Erro 503 ou 502

**Causas comuns:**
- Health check falhando
- App não está escutando na porta `$PORT`
- Crash durante o startup

**Solução:** Verifique os logs em tempo real no Render Dashboard

## 📊 Monitoramento

### Logs em Tempo Real

No Render Dashboard:
- **Logs** → Ver logs em tempo real
- Filtre por tipo: Build, Deploy, Runtime

### Métricas

O Render mostra:
- Requisições por minuto
- Tempo de resposta
- Uso de memória/CPU
- Status do health check

## 🔄 Atualizações

Para fazer updates:

1. Faça commit e push no seu repositório:
   ```bash
   git add .
   git commit -m "Update API"
   git push origin feat-adding-api
   ```

2. O Render faz deploy automático! 🚀

Ou faça deploy manual no dashboard:
- **Manual Deploy** → **Deploy latest commit**

## 📝 Link Final para Entrega

Para o Tech Challenge, use este formato no arquivo `.txt`:

```
Repositório GitHub: https://github.com/SEU-USUARIO/book-api
API em Produção: https://SEU-APP.onrender.com
Documentação Swagger: https://SEU-APP.onrender.com/docs
Vídeo Apresentação: [SEU LINK DO YOUTUBE/LOOM]
```

## ✅ Checklist Final

Antes de entregar:

- [ ] API está respondendo no Render
- [ ] Health check retorna 200
- [ ] Swagger docs está acessível
- [ ] Endpoints retornam dados corretos
- [ ] Autenticação funciona
- [ ] Link público está funcionando
- [ ] Arquivo `.txt` criado com links
- [ ] Vídeo de apresentação gravado

## 🆘 Precisa de Ajuda?

Se encontrar problemas:

1. **Verifique os logs** no Render Dashboard
2. **Teste localmente** primeiro: `uvicorn app.main:app --reload`
3. **Compare com o repositório** de exemplo
4. **Consulte a documentação**: [RENDER_SETUP.md](RENDER_SETUP.md)

---

**Boa sorte com o deploy!** 🚀

Se seguir este guia passo a passo, sua API estará online em menos de 10 minutos!
