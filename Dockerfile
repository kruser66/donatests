FROM python:3.11.3-slim-buster

WORKDIR /donate

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "donate_bot.py"]