#!/usr/bin/env python3
"""
Script de Migração CSV para SQLite
Migra dados de livros do arquivo CSV para o banco de dados SQLite
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


def migrate_books_from_csv():
    """Migra livros do CSV para o banco de dados SQLite"""

    # Caminhos dos arquivos
    csv_path = Path(__file__).parent.parent / "data" / "books.csv"

    if not csv_path.exists():
        print(f"❌ Erro: Arquivo CSV não encontrado em {csv_path}")
        return False

    print(f"📁 Lendo CSV de: {csv_path}")

    # Lê o CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ {len(df)} livros lidos com sucesso do CSV")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return False

    # Cria todas as tabelas
    print("🔧 Criando tabelas do banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas do banco de dados criadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

    # Insere livros no banco de dados
    print("📚 Inserindo livros no banco de dados...")
    db = SessionLocal()

    try:
        # Limpa livros existentes (opcional - para migração limpa)
        db.query(Book).delete()
        db.commit()

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
        print(f"✅ {inserted_count} livros inseridos com sucesso no banco de dados")

        # Verifica a inserção
        total_books = db.query(Book).count()
        print(f"📊 Total de livros no banco de dados: {total_books}")

        return True

    except Exception as e:
        print(f"❌ Erro ao inserir livros: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def print_summary():
    """Imprime resumo do banco de dados"""
    db = SessionLocal()
    try:
        total_books = db.query(Book).count()
        total_categories = db.query(Book.category).distinct().count()
        avg_price = db.query(Book.price).scalar()

        print("\n" + "=" * 50)
        print("📊 RESUMO DO BANCO DE DADOS")
        print("=" * 50)
        print(f"Total de Livros: {total_books}")
        print(f"Total de Categorias: {total_categories}")
        print(f"Banco de Dados: {engine.url}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Erro ao obter resumo: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Iniciando migração de CSV para SQLite...")
    print("=" * 50)

    success = migrate_books_from_csv()

    if success:
        print_summary()
        print("\n✅ Migração concluída com sucesso!")
    else:
        print("\n❌ Migração falhou!")
        sys.exit(1)
