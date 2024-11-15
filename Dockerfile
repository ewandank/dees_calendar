FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt /app/
COPY main.py /app/
COPY web /app/web
ADD web /app/web
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN rm /app/requirements.txt

EXPOSE 80
CMD ["fastapi", "run", "main.py", "--port", "80"]