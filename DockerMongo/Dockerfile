FROM python:3
WORKDIR /todo
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "-u", "flask_brevets.py"]