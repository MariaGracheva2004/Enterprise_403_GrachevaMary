from database import SessionLocal
import models

db = SessionLocal()

user = db.query(models.User).filter(models.User.username == "admin").first()
admin_role = db.query(models.Role).filter(models.Role.name == "ROLE_ADMIN").first()

if user and admin_role:
    user.roles.append(admin_role)
    db.commit()
    print("Готово! admin теперь администратор")

db.close()

# пароль: admin123