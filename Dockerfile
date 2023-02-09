# FROM ubuntu:20.04
# RUN apt-get update \
#     && apt-get -y install python3-pip

FROM python:3.8

WORKDIR /taxcalculator

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501 80 443

CMD ["streamlit","run","./main.py"]