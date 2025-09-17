FROM python:3.9-slim

WORKDIR /app

COPY ./TossaTicketsBot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./TossaTicketsBot .

ENV APP_ENV=prod

CMD ["sh", "-c", "python main.py $APP_ENV"]