#!/usr/bin/env python3
"""
Script de Criação de Usuário Administrador
Cria um usuário administrador para a aplicação
"""
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar os módulos da aplicação
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings


def create_admin_user():
    """Cria usuário administrador a partir das variáveis de ambiente"""

    print("🔧 Criando tabelas do banco de dados se não existirem...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Verifica se o usuário admin já existe
        existing_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()

        if existing_admin:
            print(f"⚠️  Usuário administrador '{settings.ADMIN_USERNAME}' já existe!")
            print(f"   ID do Usuário: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            print(f"   É Admin: {existing_admin.is_admin}")
            print(f"   Está Ativo: {existing_admin.is_active}")
            return

        # Cria novo usuário administrador
        # Trunca a senha para 72 bytes para compatibilidade com bcrypt
        password = settings.ADMIN_PASSWORD[:72]
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

        print("\n" + "=" * 50)
        print("✅ Usuário administrador criado com sucesso!")
        print("=" * 50)
        print(f"Usuário: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Senha: {settings.ADMIN_PASSWORD}")
        print(f"É Admin: {admin.is_admin}")
        print(f"ID do Usuário: {admin.id}")
        print("=" * 50)
        print("\n💡 Você pode fazer login com estas credenciais:")
        print(f"   POST /api/v1/auth/login")
        print(f"   username={admin.username}&password={settings.ADMIN_PASSWORD}")
        print()

    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Script de Criação de Usuário Administrador")
    print("=" * 50)
    create_admin_user()
