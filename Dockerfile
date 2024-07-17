FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install .

EXPOSE 8000

CMD ["python3", "./src/app/main.py"]