# Docker-команда FROM указывает базовый образ контейнера
# Наш базовый образ - это Linux с предустановленным python-3.10
FROM python:3.10

# Установим переменную окружения
ENV APP_HOME /app
ENV DATA_DIR /data
VOLUME /data

# Установим рабочую директорию внутри контейнера
WORKDIR $APP_HOME

# Скопируем файлы pyproject.toml и poetry.lock в рабочую директорию контейнера
COPY pyproject.toml poetry.lock ./

# Установим Poetry
RUN pip install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Установим зависимости с помощью Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Скопируем остальные файлы в рабочую директорию контейнера
COPY . .

# Обозначим порт где работает приложение внутри контейнера
EXPOSE 5000

# Создаем каталог storage и копируем data.json
RUN mkdir -p /data
COPY storage/data.json /data/data.json

# Определяем точку входа для запуска приложения
ENTRYPOINT ["poetry", "run", "python", "main.py"]
