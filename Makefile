clear:
	docker-compose rm -f

down:
	docker-compose down -v

local:
	@docker-compose up --d db
	@sleep 10
	@docker-compose up --build --d server
	@docker-compose exec server python manage.py migrate


test:
	@sleep 4
	@echo "gigigigi"