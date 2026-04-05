from database import engine
from models import Base, Role
from sqlalchemy import inspect

Base.metadata.create_all(bind=engine)
print("Таблицы созданы!")

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Таблицы в БД: {tables}")

from database import SessionLocal
db = SessionLocal()

for name in ["ROLE_USER", "ROLE_ADMIN"]:
    existing = db.query(Role).filter(Role.name == name).first()
    if not existing:
        db.add(Role(name=name))
        print(f"Роль {name} добавлена")
    else:
        print(f"Роль {name} уже существует")

db.commit()
db.close()