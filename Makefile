install:
	pip install -r requirements.txt

db:
	docker compose up -d db

init:
	python scripts/init_db.py

run:
	uvicorn app.main:app --reload

test:
	pytest -q
