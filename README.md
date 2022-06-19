# Mega Market Open API

Вступительное задание в Летнюю Школу Бэкенд Разработки Яндекса 2022

### Как запустить проект в контейнере:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:bikrtw/enrollment.git
cd enrollment
```

Перейти в директорию, содержащую файл docker-compose.yaml:

```
cd docker
```

Запустить docker-compose

```
docker-compose up -d
```

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

Профит!

## Содержимое файла .env:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
