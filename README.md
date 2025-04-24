# Guida all'Installazione e Configurazione di MetaTrader Remote Control

## Panoramica

MetaTrader Remote Control è una soluzione completa per il controllo remoto di diverse istanze di MetaTrader 5 installate su server Windows. La soluzione è composta da tre componenti principali:

1. **Agente MetaTrader** - Un'applicazione Python che si installa sui server Windows dove sono presenti le istanze di MetaTrader 5
2. **Server Centrale** - Un backend Flask che funge da hub centrale
3. **Interfaccia Web** - Un'interfaccia utente web per il controllo centralizzato

## Requisiti di Sistema

### Server Centrale e Interfaccia Web
- Docker e Docker Compose
- Accesso a Internet
- Porte 80 (HTTP) e 5000 (API) aperte

### Server Windows con MetaTrader 5
- Windows Server 2016 o superiore
- MetaTrader 5 installato
- Python 3.8 o superiore
- Docker Desktop per Windows (opzionale)
- Accesso a Internet
- Porta 5001 aperta

## Installazione

### 1. Installazione del Server Centrale e dell'Interfaccia Web

1. Clona il repository o copia i file sul server:
   ```bash
   git clone <repository-url> metatrader_remote_control
   cd metatrader_remote_control
   ```

2. Modifica le credenziali di autenticazione nel file `docker-compose.yml`:
   ```yaml
   environment:
     - SECRET_KEY=your_secret_key_here
     - AUTH_USERNAME=admin
     - AUTH_PASSWORD=secure_password_here
   ```

3. Avvia i container Docker:
   ```bash
   docker-compose up -d backend frontend
   ```

4. Verifica che i servizi siano in esecuzione:
   ```bash
   docker-compose ps
   ```

### 2. Installazione dell'Agente MetaTrader sui Server Windows

Per ciascuno dei tuoi 3 server Windows con MetaTrader 5:

1. Installa Python 3.8 o superiore se non è già installato

2. Copia la cartella `agent` sul server Windows

3. Installa le dipendenze:
   ```bash
   cd agent
   pip install -r requirements.txt
   ```

4. Modifica il file `agent_config.json` (verrà creato al primo avvio) per specificare il percorso di MetaTrader 5:
   ```json
   {
     "mt5_path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
     "accounts": []
   }
   ```

5. Avvia l'agente:
   ```bash
   python agent.py
   ```

   Oppure, se preferisci usare Docker:
   ```bash
   docker build -t metatrader-agent .
   docker run -d -p 5001:5001 -v C:/path/to/MetaTrader5:/mt5 --name metatrader-agent metatrader-agent
   ```

6. Configura l'agente come servizio Windows per garantire che si avvii automaticamente:
   ```bash
   # Usando NSSM (Non-Sucking Service Manager)
   nssm install MetaTraderAgent "C:\path\to\python.exe" "C:\path\to\agent.py"
   nssm start MetaTraderAgent
   ```

## Configurazione

### 1. Accesso all'Interfaccia Web

1. Apri un browser e vai all'indirizzo del server centrale (es. http://server-ip)
2. Accedi con le credenziali configurate nel file `docker-compose.yml`

### 2. Registrazione dei Server

1. Vai alla sezione "Server" nell'interfaccia web
2. Clicca su "Aggiungi Server"
3. Inserisci un nome per il server e l'URL dell'agente (es. http://server-windows-ip:5001)
4. Clicca su "Aggiungi"

### 3. Registrazione degli Account MetaTrader

1. Vai alla sezione "Account" nell'interfaccia web
2. Clicca su "Aggiungi Account"
3. Seleziona il server, inserisci il numero di account, la password, il nome del server MT5 e una descrizione
4. Clicca su "Aggiungi"

### 4. Configurazione Master-Slave

1. Vai alla sezione "Master-Slave" nell'interfaccia web
2. Clicca su "Aggiungi Configurazione"
3. Seleziona l'account master
4. Aggiungi uno o più account slave, specificando:
   - Rapporto di dimensione (es. 1.0 per la stessa dimensione)
   - Direzione (stessa o opposta)
   - Se utilizzare stop loss e take profit
5. Clicca su "Aggiungi"

## Utilizzo

### Visualizzazione dei Dati

- La dashboard mostra una panoramica di tutti i server, account e posizioni
- Clicca su un account per visualizzare i dettagli, inclusi saldo, posizioni aperte e cronologia

### Apertura di Posizioni

1. Seleziona un account
2. Clicca su "Apri Posizione"
3. Inserisci i dettagli dell'ordine:
   - Simbolo (es. EURUSD)
   - Tipo (Buy o Sell)
   - Volume
   - Stop Loss e Take Profit (opzionali)
   - Prezzo limite (opzionale, per ordini limite)
4. Clicca su "Apri Posizione"

Se l'account è configurato come master, l'operazione verrà propagata agli account slave secondo le configurazioni impostate.

### Chiusura di Posizioni

1. Seleziona un account
2. Visualizza le posizioni aperte
3. Clicca su "Chiudi" accanto alla posizione che desideri chiudere

Oppure, per chiudere tutte le posizioni:
1. Seleziona un account
2. Clicca su "Chiudi Tutte le Posizioni"

## Funzionalità Avanzate

### Ordini Limite con Fallback a Market

Quando apri una posizione su un account master con un ordine limite, gli account slave tenteranno di eseguire lo stesso tipo di ordine. Se l'ordine limite non può essere eseguito su un account slave, il sistema eseguirà automaticamente un ordine market come fallback.

### Aggiunta di Nuovi Gruppi di MetaTrader

Per aggiungere un nuovo gruppo di MetaTrader:
1. Installa l'agente MetaTrader sul nuovo server Windows
2. Registra il nuovo server nell'interfaccia web
3. Aggiungi gli account MetaTrader associati
4. Configura le relazioni master-slave se necessario

## Risoluzione dei Problemi

### L'agente non si connette a MetaTrader 5

1. Verifica che MetaTrader 5 sia installato nel percorso specificato in `agent_config.json`
2. Assicurati che le credenziali dell'account siano corrette
3. Controlla i log dell'agente per errori specifici

### Il server centrale non comunica con l'agente

1. Verifica che la porta 5001 sia aperta sul server Windows
2. Controlla che l'URL dell'agente sia corretto nell'interfaccia web
3. Verifica che l'agente sia in esecuzione

### Problemi con gli ordini

1. Controlla che il simbolo sia corretto e disponibile sul broker
2. Verifica che ci sia sufficiente margine disponibile
3. Controlla i log dell'agente per errori specifici

## Manutenzione

### Backup della Configurazione

Il server centrale salva la configurazione in un file `config.json`. È consigliabile eseguire regolarmente il backup di questo file:

```bash
docker cp metatrader_remote_control_backend_1:/app/config.json ./config_backup.json
```

### Aggiornamento del Software

1. Ferma i container:
   ```bash
   docker-compose down
   ```

2. Aggiorna i file del progetto

3. Ricostruisci e riavvia i container:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Sicurezza

La soluzione implementa un'autenticazione HTTP Basic per proteggere l'accesso all'interfaccia web e alle API. È consigliabile:

1. Utilizzare HTTPS invece di HTTP in produzione
2. Cambiare regolarmente le password
3. Limitare l'accesso alle porte utilizzate solo agli IP necessari
4. Utilizzare un firewall per proteggere i server

## Supporto

Per assistenza o segnalazione di problemi, contattare il supporto tecnico.
