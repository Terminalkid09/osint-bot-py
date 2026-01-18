FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il progetto
COPY . .

# Avvia il bot
CMD ["python", "bot.py"]