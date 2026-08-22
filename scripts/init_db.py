from sqlalchemy import text
from app.db import engine,Base
import app.models
with engine.begin() as c:c.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
Base.metadata.create_all(engine)
print("Database initialized.")
