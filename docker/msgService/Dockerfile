# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /src
ENV FLASK_APP=msgServer.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY msgServer.py msgServer.py
EXPOSE 4000
CMD ["flask", "run", "--port=4000"]