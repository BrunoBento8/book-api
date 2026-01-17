# ✅ Checklist de Deploy - Render.com

Use este checklist enquanto faz o deploy para não esquecer nada!

## 🎯 Antes de Começar

- [ ] Código está no GitHub e atualizado
- [ ] Arquivo `data/books.csv` está no repositório (1000 livros)
- [ ] Branch principal está limpa e funcional
- [ ] Testei localmente com `uvicorn app.main:app --reload`
- [ ] Conta criada no [Render.com](https://dashboard.render.com)

## 🔗 Passo 1: Conectar Repositório

- [ ] Acessei https://dashboard.render.com
- [ ] Cliquei em "New +" → "Web Service"
- [ ] Conectei minha conta do GitHub
- [ ] Selecionei o repositório `book-api`
- [ ] Cliquei em "Connect"

## ⚙️ Passo 2: Configurações Básicas

- [ ] **Name**: `book-recommendation-api` (ou similar)
- [ ] **Region**: Oregon (US West) ou mais próximo
- [ ] **Branch**: `feat-adding-api` ou `main`
- [ ] **Runtime**: Python 3
- [ ] **Plan**: Free

## 🔨 Passo 3: Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && mkdir -p data && python scripts/init_database.py
```
- [ ] Build command copiado e colado corretamente

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- [ ] Start command copiado e colado corretamente

## 🔐 Passo 4: Variáveis de Ambiente

Copie e cole estas variáveis (ajuste se necessário):

```
APP_NAME=book-recommendation-api
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=sqlite:///./data/books.db
SECRET_KEY=sua-chave-super-secreta-altere-em-producao-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["*"]
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@bookapi.com
ADMIN_PASSWORD=Admin@123
```

**Checklist de variáveis:**
- [ ] `APP_NAME` adicionado
- [ ] `APP_VERSION` adicionado
- [ ] `ENVIRONMENT` = production
- [ ] `DEBUG` = False
- [ ] `DATABASE_URL` adicionado
- [ ] `SECRET_KEY` adicionado e marcado como **Secret** 🔒
- [ ] `ALGORITHM` adicionado
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` adicionado
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS` adicionado
- [ ] `ALLOWED_ORIGINS` adicionado
- [ ] `ADMIN_USERNAME` adicionado
- [ ] `ADMIN_EMAIL` adicionado
- [ ] `ADMIN_PASSWORD` adicionado e marcado como **Secret** 🔒

**⚠️ CRÍTICO:**
- [ ] Marquei `SECRET_KEY` como **Secret**
- [ ] Marquei `ADMIN_PASSWORD` como **Secret**
- [ ] Usei senha forte para `ADMIN_PASSWORD`

## 💾 Passo 5: Disco Persistente

Na seção **"Advanced"**:

- [ ] Cliquei em "Add Disk"
- [ ] **Name**: `data-disk`
- [ ] **Mount Path**: `/opt/render/project/src/data`
- [ ] **Size**: `1 GB`

## 🏥 Passo 6: Health Check

- [ ] **Health Check Path**: `/api/v1/health`

## 🚀 Passo 7: Deploy!

- [ ] Revisei todas as configurações acima
- [ ] Cliquei em "Create Web Service"
- [ ] Aguardei o build iniciar (pode levar 3-5 minutos)

## 📊 Passo 8: Monitorar Build

No Render Dashboard, aba **"Logs"**, procure por:

- [ ] `✅ Successfully installed ...` (dependências)
- [ ] `✅ Tabelas criadas: api_logs, books, users`
- [ ] `✅ 1000 livros importados com sucesso`
- [ ] `✅ Admin criado com sucesso!`
- [ ] `✅ INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!`
- [ ] Build status: **"Live"** (verde) 🟢

## 🧪 Passo 9: Testes

**Anote sua URL do Render:**
```
https://_____________________________.onrender.com
```

### Teste 1: Health Check
```bash
curl https://SEU-APP.onrender.com/api/v1/health
```
- [ ] Retornou JSON com `"status": "saudável"`
- [ ] Status code 200

### Teste 2: Swagger Docs
Abra no navegador:
```
https://SEU-APP.onrender.com/docs
```
- [ ] Página Swagger abriu corretamente
- [ ] Mostra 15 endpoints

### Teste 3: Listar Livros
```bash
curl https://SEU-APP.onrender.com/api/v1/books
```
- [ ] Retornou array com livros
- [ ] Tem paginação

### Teste 4: Autenticação
```bash
curl -X POST "https://SEU-APP.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin@123"
```
- [ ] Retornou `access_token` e `refresh_token`
- [ ] Status code 200

### Teste 5: Categorias
```bash
curl https://SEU-APP.onrender.com/api/v1/categories
```
- [ ] Retornou lista de categorias
- [ ] Tem contagem de livros

### Teste 6: Estatísticas
```bash
curl https://SEU-APP.onrender.com/api/v1/stats/overview
```
- [ ] Retornou estatísticas gerais
- [ ] Mostra total de livros

## 📝 Passo 10: Documentar Links

**Para entregar no Tech Challenge**, crie arquivo `links_entrega.txt`:

```
========================================
TECH CHALLENGE - FASE 1
Engenharia de Machine Learning
========================================

ALUNO: [SEU NOME]
RM: [SEU RM]

========================================
LINKS DO PROJETO
========================================

Repositório GitHub:
https://github.com/[SEU-USUARIO]/book-api

API em Produção (Render):
https://[SEU-APP].onrender.com

Documentação Swagger:
https://[SEU-APP].onrender.com/docs

ReDoc:
https://[SEU-APP].onrender.com/redoc

Vídeo de Apresentação:
https://[YOUTUBE/LOOM/DRIVE]

========================================
CREDENCIAIS DE TESTE
========================================

Username: admin
Password: Admin@123

========================================
ENDPOINTS PRINCIPAIS
========================================

Health Check:
GET https://[SEU-APP].onrender.com/api/v1/health

Listar Livros:
GET https://[SEU-APP].onrender.com/api/v1/books

Buscar Livros:
GET https://[SEU-APP].onrender.com/api/v1/books/search?title=light

Categorias:
GET https://[SEU-APP].onrender.com/api/v1/categories

Estatísticas:
GET https://[SEU-APP].onrender.com/api/v1/stats/overview

Login:
POST https://[SEU-APP].onrender.com/api/v1/auth/login

ML Features:
GET https://[SEU-APP].onrender.com/api/v1/ml/features

========================================
DESAFIOS BÔNUS IMPLEMENTADOS
========================================

✅ Desafio 1: Sistema de Autenticação JWT
   - Login com OAuth2
   - Access e Refresh tokens
   - Rotas protegidas

✅ Desafio 2: Pipeline ML-Ready
   - Features engenheiradas
   - Export de training data
   - Endpoint de predições

✅ Desafio 3: Monitoramento & Analytics
   - Logging estruturado
   - Dashboard Streamlit
   - Métricas em tempo real

========================================
DADOS DO DEPLOY
========================================

Plataforma: Render.com (Free Tier)
Runtime: Python 3.11
Framework: FastAPI
Banco de Dados: SQLite (1000 livros)
Região: Oregon (US West)

========================================
```

- [ ] Criei o arquivo `links_entrega.txt`
- [ ] Preenchi todos os campos
- [ ] Testei todos os links

## 🎬 Passo 11: Vídeo de Apresentação

**Roteiro sugerido (3-12 minutos):**

1. **Introdução (30s)**
   - [ ] Apresentação pessoal
   - [ ] Objetivo do projeto

2. **Demonstração da API (2-3min)**
   - [ ] Acessar Swagger docs
   - [ ] Mostrar endpoints principais
   - [ ] Fazer requisição GET /books
   - [ ] Fazer login e obter token
   - [ ] Testar endpoint protegido

3. **Arquitetura (2-3min)**
   - [ ] Explicar pipeline de dados
   - [ ] Web scraping → CSV → Database → API
   - [ ] Mostrar estrutura do projeto
   - [ ] Explicar tecnologias usadas

4. **Desafios Bônus (2-3min)**
   - [ ] Demonstrar autenticação JWT
   - [ ] Mostrar endpoints ML
   - [ ] Demonstrar dashboard de monitoramento

5. **Deployment (1-2min)**
   - [ ] Mostrar API rodando no Render
   - [ ] Explicar configurações
   - [ ] Mostrar logs

6. **Conclusão (30s)**
   - [ ] Resumir principais features
   - [ ] Agradecer

**Ferramentas de gravação:**
- [ ] Loom (recomendado)
- [ ] OBS Studio
- [ ] Zoom
- [ ] Ou outro de sua preferência

- [ ] Vídeo gravado
- [ ] Upload feito (YouTube/Loom/Drive)
- [ ] Link público obtido
- [ ] Link testado (abre para qualquer pessoa)

## 📤 Passo 12: Entrega Final

- [ ] Arquivo `links_entrega.txt` criado
- [ ] Todos os links funcionando
- [ ] Vídeo acessível publicamente
- [ ] README.md atualizado com link do deploy
- [ ] Código final no GitHub
- [ ] Pronto para submeter!

## 🎉 Deploy Completo!

Se todos os itens acima estão marcados, **PARABÉNS!** 🚀

Sua API está:
- ✅ Rodando em produção
- ✅ Acessível publicamente
- ✅ Totalmente funcional
- ✅ Documentada
- ✅ Pronta para entrega

## 🆘 Se algo deu errado...

**Problema com Build:**
1. Vá em "Manual Deploy" → "Clear build cache & deploy"
2. Verifique logs de build
3. Confirme que `requirements.txt` e `scripts/init_database.py` existem

**Problema com Health Check:**
1. Verifique que endpoint `/api/v1/health` existe
2. Confirme que app usa porta `$PORT`
3. Veja logs em runtime

**Problema com Database:**
1. Confirme que disco persistente foi adicionado
2. Verifique que mount path está correto
3. Veja logs do `init_database.py`

**Problema com Autenticação:**
1. Confirme que `ADMIN_PASSWORD` está configurado
2. Verifique logs de criação do admin
3. Tente fazer rebuild

**API está lenta:**
- Normal! Plano free hiberna após 15min
- Primeira requisição leva 30-60s
- Próximas são rápidas

## 📞 Suporte Adicional

**Documentação do projeto:**
- [DEPLOY_RENDER_QUICKSTART.md](DEPLOY_RENDER_QUICKSTART.md) - Guia passo a passo
- [DEPLOY_VISUAL_GUIDE.md](DEPLOY_VISUAL_GUIDE.md) - Diagramas e visualizações
- [RENDER_SETUP.md](RENDER_SETUP.md) - Documentação detalhada
- [README.md](README.md) - Documentação completa do projeto

**Recursos online:**
- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Boa sorte com o deploy e com o Tech Challenge!** 🚀🎓

*Última atualização: 2026-01-17*
