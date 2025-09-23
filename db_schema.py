from sqlalchemy import create_engine, inspect
from app.core.config import settings

eng = create_engine(settings.database_url)
insp = inspect(eng)
for c in insp.get_columns("uploads"):
    print(c["name"], c["type"])
