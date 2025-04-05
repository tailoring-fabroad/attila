# source .env && make run -> jika env gagal di load

run:
	@poetry install
	@poetry shell
	@uvicorn app.main:app --reload

migrate:
	# @alembic revision --autogenerate -m "auto-migrate"
	@alembic upgrade head
