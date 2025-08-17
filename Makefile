.PHONY: up down deps seed etl api test

up:
\tdocker compose up -d

down:
\tdocker compose down -v

deps:
\tpython -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

api:
\t. .venv/bin/activate && uvicorn api.main:app --reload

etl:
\t. .venv/bin/activate && python etl/run.py

seed:
\t. .venv/bin/activate && python etl/seed_data.py

test:
\t. .venv/bin/activate && pytest -q
