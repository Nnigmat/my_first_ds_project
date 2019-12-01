FROM python:3.7-alpine
RUN pip3 install --no-cache-dir flask requests
WORKDIR /app
COPY ./ /app
EXPOSE 8080
CMD python3 app.py