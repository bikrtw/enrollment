FROM python:3.7-slim

RUN mkdir /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

WORKDIR /app

# Выполнить запуск сервера разработки при старте контейнера.
CMD ["gunicorn", "mega_market.wsgi:application", "--bind", "0:8000" ]