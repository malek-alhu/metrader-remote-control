# Usa l'immagine ufficiale di Python
FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dell'applicazione
COPY . .

# Esponi la porta su cui l'applicazione sarà in ascolto
EXPOSE 5000

# Comando per avviare l'applicazione
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
