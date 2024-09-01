FROM python:3.10-alpine
WORKDIR /
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
CMD python app.py
