# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /src
ENV FLASK_APP=forumServer.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY forumServer.py forumServer.py
EXPOSE 3000
CMD ["flask", "run", "--port=3000"]