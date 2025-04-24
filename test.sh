#!/bin/bash

# Script di test per la soluzione di controllo remoto di MetaTrader 5

echo "Iniziando il test della soluzione di controllo remoto di MetaTrader 5..."

# Verifica che Docker sia installato
if ! command -v docker &> /dev/null; then
    echo "Docker non è installato. Installalo prima di procedere."
    exit 1
fi

# Verifica che Docker Compose sia installato
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose non è installato. Installalo prima di procedere."
    exit 1
fi

# Crea una directory per i test
mkdir -p test_results

echo "1. Test del backend API..."
# Costruisci e avvia solo il backend per i test
docker-compose build backend
docker-compose up -d backend

# Attendi che il backend sia pronto
sleep 5

# Test dell'endpoint principale
echo "Test dell'endpoint principale..."
curl -u admin:secure_password_here http://localhost:5000/ > test_results/backend_root.json
if [ $? -eq 0 ]; then
    echo "✅ Test dell'endpoint principale completato con successo"
else
    echo "❌ Test dell'endpoint principale fallito"
fi

# Test della registrazione di un server
echo "Test della registrazione di un server..."
curl -u admin:secure_password_here -X POST -H "Content-Type: application/json" -d '{"name":"Test Server","url":"http://localhost:5001"}' http://localhost:5000/api/servers > test_results/server_registration.json
if [ $? -eq 0 ]; then
    echo "✅ Test della registrazione di un server completato con successo"
else
    echo "❌ Test della registrazione di un server fallito"
fi

# Test del recupero dei server
echo "Test del recupero dei server..."
curl -u admin:secure_password_here http://localhost:5000/api/servers > test_results/servers_list.json
if [ $? -eq 0 ]; then
    echo "✅ Test del recupero dei server completato con successo"
else
    echo "❌ Test del recupero dei server fallito"
fi

# Arresta il backend
docker-compose stop backend

echo "2. Test dell'agente MetaTrader..."
echo "Nota: I test completi dell'agente richiedono un'installazione di MetaTrader 5 su Windows."
echo "Questi test dovrebbero essere eseguiti su un server Windows con MetaTrader 5 installato."

echo "3. Test del frontend..."
# Costruisci e avvia il frontend per i test
docker-compose build frontend
docker-compose up -d frontend

# Attendi che il frontend sia pronto
sleep 5

# Verifica che il frontend sia accessibile
echo "Verifica che il frontend sia accessibile..."
curl -s -o /dev/null -w "%{http_code}" http://localhost > test_results/frontend_status.txt
if [ $? -eq 0 ]; then
    echo "✅ Frontend accessibile"
else
    echo "❌ Frontend non accessibile"
fi

# Arresta il frontend
docker-compose stop frontend

echo "4. Test dell'integrazione completa..."
echo "Nota: I test di integrazione completa richiedono un'installazione di MetaTrader 5 su Windows."
echo "Questi test dovrebbero essere eseguiti in un ambiente con tutti i componenti configurati."

# Arresta tutti i container
docker-compose down

echo "Test completati. I risultati sono disponibili nella directory 'test_results'."
