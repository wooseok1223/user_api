# user_api
login with user api

## 1 스펙
SERVER : Django, Django-rest-framework

DB : Mysql

### 상세 스펙

#### 로그인 
- login JWT token 이용 common/backends.py (BaseAuthentication 상속받음)

#### 인증
- 인증 방식 auth 테이블에 토큰값 저장
- sms 방식 대신 get api 호출하여 토큰값 확인

#### 회원가입
- 토큰 param(auth_number)을 받아야 회원가입가능 (유효시간 5분)

#### api-document 적용
아래의 로컬 구동 후 접속 가능
- http://localhost:8000/swagger/

## 2 로컬테스트 환경 구성
docker-compose를 이용하여 mysql, api-server를 띄울수 있게 구성

<h3>로컬에 도커가 설치되어있어야한다.</h3>

## 2-1 환경변수
django-dotenv 외부 라이브러리 이용중

user_api와 하위 경로에 .env파일에 환경변수를 세팅해줘야함

## 2-3 매크로정의 툴
Makefile을 사용하여 명령어 셋업 툴 구성

<ul>
<li>@docker-compose up --d db</li>
<li>@sleep 10</li>
<li>@docker-compose up --build --d server</li>
<li>@docker-compose exec server python manage.py migrate</li>
</ul>

## 2-4 로컬 실행
make local 명령어를 통해서 서버 실행

![result](base/img/docker.png)


## 3-1 api 기능



