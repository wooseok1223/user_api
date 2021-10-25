clear:
	docker-compose rm -f

down:
	docker-compose down -v

local:
	@docker-compose up --d db
	@sleep 10
	@docker-compose up --build --d server
	@docker-compose exec server python manage.py migrate
	@echo "테스트 코드 실행"
	@docker-compose exec server python manage.py test
	@echo "테스트 코드 성공"
