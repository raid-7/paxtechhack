FROM openjdk:11.0-jdk-slim-stretch

RUN apt-get install -y python3 python3-pip nano htop
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY backend /app
COPY generator.py /app

WORKDIR /app/backend/server-main
RUN mvn clean install

WORKDIR /app
CMD java --add-modules java.xml.bind -jar backend/server-main/target/server-main-1.0-SNAPSHOT.jar
