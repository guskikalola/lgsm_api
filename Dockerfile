FROM ubuntu:latest
WORKDIR /app
COPY . .
RUN sh install.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]
EXPOSE 8000