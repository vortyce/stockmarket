from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
db.execute(text("UPDATE alembic_version SET version_num = '6e596b4cf88c'"))
db.commit()
print("Alembic version reset to 6e596b4cf88c")
db.close()
