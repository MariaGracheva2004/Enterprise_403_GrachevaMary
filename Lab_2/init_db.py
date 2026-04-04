from database import SessionLocal, engine
import models

def init_db():
    
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        
        role_names = ["ROLE_USER", "ROLE_ADMIN"]
        
        for name in role_names:
            
            existing_role = db.query(models.Role).filter(models.Role.name == name).first()
            if not existing_role:
                new_role = models.Role(name=name)
                db.add(new_role)
                print(f"Роль {name} добавлена.")
            else:
                print(f"Роль {name} уже существует.")
        
        db.commit()
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()