FROM maven:3.6.0-jdk-10-slim

RUN apt-get update && apt-get install -y python3 python3-pip nano htop

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY backend/ /app/backend
COPY generator.py /app

WORKDIR /app/backend/server-main
RUN mvn clean install

WORKDIR /app
CMD java --add-modules java.se.ee -jar backend/server-main/target/server-main-1.0-SNAPSHOT.jar
