FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APP_ENV=dev

EXPOSE 8000

CMD ["sh", "-c", "python main.py $APP_ENV"]