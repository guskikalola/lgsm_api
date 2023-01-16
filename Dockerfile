FROM python:alpine
WORKDIR /app
COPY build .
COPY src ./src
RUN sh install.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]
EXPOSE 8000