.PHONY: install backend frontend dev test lint demo seed

install:
	python -m pip install -e backend[dev]
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

dev:
	@echo "Run backend and frontend in separate terminals: make backend / make frontend"

test:
	cd backend && pytest -q
	cd frontend && npm run test

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint || true

demo:
	bash scripts/demo.sh

seed:
	python scripts/seed_data.py
