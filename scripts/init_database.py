#!/usr/bin/env python3
"""
Script de Inicialização do Banco de Dados
Inicializa o banco de dados SQLite com tabelas, dados e usuário admin.

Este script é projetado para ser robusto e não falhar se algumas etapas
já foram completadas ou se arquivos opcionais não existem.

Uso:
    python scripts/init_database.py

Variáveis de Ambiente Necessárias:
    - ADMIN_USERNAME: Username do administrador
    - ADMIN_EMAIL: Email do administrador
    - ADMIN_PASSWORD: Senha do administrador
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Adiciona o diretório pai ao path para importar módulos da aplicação
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, Base
from app.models.book import Book
from app.models.user import User
from app.models.api_log import APILog
from app.utils.security import get_password_hash
from app.config import settings


def create_data_directory():
    """Cria o diretório data/ se não existir"""
    data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        print(f"📁 Criando diretório de dados: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Diretório criado com sucesso")
    else:
        print(f"✅ Diretório de dados já existe: {data_dir}")

    return data_dir


def create_database_tables():
    """Cria todas as tabelas do banco de dados"""
    print("\n🔧 Criando tabelas do banco de dados...")

    try:
        # Importa todos os modelos para garantir que estão registrados
        from app.models import book, user, api_log

        # Cria todas as tabelas
        Base.metadata.create_all(bind=engine)

        # Verifica quais tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"✅ Tabelas criadas: {', '.join(tables)}")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_books_from_csv(data_dir):
    """Migra livros do CSV para o banco de dados"""
    csv_path = data_dir / "books.csv"

    if not csv_path.exists():
        print(f"\n⚠️  Arquivo CSV não encontrado: {csv_path}")
        print("   Pulando importação de livros. Execute o scraper para gerar o CSV.")
        return False

    print(f"\n📚 Importando livros de: {csv_path}")

    db = SessionLocal()
    try:
        # Lê o CSV
        df = pd.read_csv(csv_path)
        print(f"   Lidos {len(df)} livros do CSV")

        # Verifica se já existem livros no banco
        existing_count = db.query(Book).count()

        if existing_count > 0:
            print(f"   ⚠️  Banco já contém {existing_count} livros")
            print(f"   Pulando importação para evitar duplicatas")
            return True

        # Insere livros no banco
        inserted_count = 0
        for _, row in df.iterrows():
            book = Book(
                id=int(row['id']),
                title=str(row['title']),
                price=float(row['price']),
                rating=int(row['rating']),
                availability=int(row['availability']),
                category=str(row['category']),
                image_url=str(row['image_url']) if pd.notna(row['image_url']) else None
            )
            db.add(book)
            inserted_count += 1

        db.commit()
        print(f"✅ {inserted_count} livros importados com sucesso")

        return True

    except Exception as e:
        print(f"❌ Erro ao importar livros: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


def create_admin_user():
    """Cria usuário administrador"""
    print("\n👤 Criando usuário administrador...")

    db = SessionLocal()
    try:
        # Verifica se admin já existe
        existing_admin = db.query(User).filter(
            User.username == settings.ADMIN_USERNAME
        ).first()

        if existing_admin:
            print(f"   ⚠️  Admin '{settings.ADMIN_USERNAME}' já existe")
            print(f"   ID: {existing_admin.id}, Email: {existing_admin.email}")
            print(f"   Admin: {existing_admin.is_admin}, Ativo: {existing_admin.is_active}")
            return True

        # Verifica se variáveis de ambiente estão configuradas
        if not settings.ADMIN_PASSWORD:
            print("   ❌ ADMIN_PASSWORD não está configurado!")
            print("   Configure a variável de ambiente ADMIN_PASSWORD")
            return False

        # Cria novo admin
        password = settings.ADMIN_PASSWORD[:72]  # Bcrypt limit
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Admin criado com sucesso!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   ID: {admin.id}")

        return True

    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


def print_database_summary():
    """Imprime resumo do banco de dados"""
    db = SessionLocal()
    try:
        total_books = db.query(Book).count()
        total_users = db.query(User).count()
        total_admins = db.query(User).filter(User.is_admin == True).count()

        print("\n" + "=" * 60)
        print("📊 RESUMO DO BANCO DE DADOS")
        print("=" * 60)
        print(f"Database URL: {engine.url}")
        print(f"Total de Livros: {total_books}")
        print(f"Total de Usuários: {total_users}")
        print(f"Total de Admins: {total_admins}")

        if total_books > 0:
            total_categories = db.query(Book.category).distinct().count()
            print(f"Total de Categorias: {total_categories}")

        print("=" * 60)

    except Exception as e:
        print(f"⚠️  Erro ao obter resumo: {e}")

    finally:
        db.close()


def verify_database():
    """Verifica se o banco de dados está funcional"""
    print("\n🔍 Verificando banco de dados...")

    db = SessionLocal()
    try:
        # Tenta fazer uma query simples
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("✅ Banco de dados está acessível")

        # Verifica se as tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = ['books', 'users', 'api_logs']
        missing_tables = [t for t in required_tables if t not in tables]

        if missing_tables:
            print(f"⚠️  Tabelas faltando: {', '.join(missing_tables)}")
            return False
        else:
            print(f"✅ Todas as tabelas necessárias existem: {', '.join(tables)}")
            return True

    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

    finally:
        db.close()


def main():
    """Função principal de inicialização"""
    print("\n" + "=" * 60)
    print("🚀 INICIALIZAÇÃO DO BANCO DE DADOS")
    print("=" * 60)

    success = True

    # Etapa 1: Criar diretório de dados
    try:
        data_dir = create_data_directory()
    except Exception as e:
        print(f"❌ Falha ao criar diretório: {e}")
        return 1

    # Etapa 2: Criar tabelas
    if not create_database_tables():
        print("\n⚠️  Aviso: Falha ao criar tabelas")
        success = False

    # Etapa 3: Verificar banco
    if not verify_database():
        print("\n❌ Banco de dados não está funcional")
        return 1

    # Etapa 4: Migrar livros do CSV (opcional)
    try:
        migrate_books_from_csv(data_dir)
    except Exception as e:
        print(f"⚠️  Aviso: Falha ao importar livros: {e}")
        # Não é fatal, continua

    # Etapa 5: Criar admin
    if not create_admin_user():
        print("\n⚠️  Aviso: Falha ao criar admin")
        success = False

    # Etapa 6: Imprimir resumo
    try:
        print_database_summary()
    except Exception as e:
        print(f"⚠️  Aviso: Falha ao gerar resumo: {e}")

    # Resultado final
    print("\n" + "=" * 60)
    if success:
        print("✅ INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("⚠️  INICIALIZAÇÃO CONCLUÍDA COM AVISOS")
        print("   Verifique os logs acima para mais detalhes")
    print("=" * 60 + "\n")

    # Retorna 0 para não falhar o build no Render
    # Mesmo com avisos, o banco básico está funcional
    return 0


if __name__ == "__main__":
    sys.exit(main())
