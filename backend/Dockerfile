FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ curl git \
    dpkg apt-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7070

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7070", "--reload"]
