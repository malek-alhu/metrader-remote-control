# Architettura Semplificata per il Controllo Remoto di MetaTrader 5

## Panoramica
Questa soluzione permette di controllare centralmente diverse istanze di MetaTrader 5 installate su server Windows, con la possibilità di configurare relazioni master-slave e gestire facilmente l'aggiunta di nuovi gruppi di MetaTrader.

## Componenti Principali

### 1. Agenti MetaTrader (su ogni server Windows)
- **Script Python locale** che utilizza la libreria MetaTrader5 per Python
- Funzionalità:
  - Connessione alle istanze locali di MetaTrader 5
  - Recupero di informazioni su saldo, posizioni aperte e cronologia
  - Esecuzione di operazioni di trading (apertura/chiusura posizioni)
  - Impostazione di stop loss e take profit
  - Esposizione di queste funzionalità tramite API REST locale

### 2. Server Centrale (Web)
- **Backend Flask** che funge da hub centrale
- Funzionalità:
  - Registrazione e gestione di tutti i server MetaTrader
  - Comunicazione con gli agenti MetaTrader sui vari server
  - Implementazione della logica master-slave
  - API REST per l'interfaccia utente

### 3. Interfaccia Utente Web
- **Frontend web** per il controllo e il monitoraggio
- Funzionalità:
  - Visualizzazione di tutte le istanze MetaTrader registrate
  - Dashboard con informazioni su saldo, posizioni e cronologia
  - Controlli per la gestione delle operazioni di trading
  - Configurazione delle relazioni master-slave
  - Aggiunta facile di nuovi server/gruppi di MetaTrader

## Flusso di Comunicazione
1. L'utente interagisce con l'interfaccia web
2. L'interfaccia web comunica con il server centrale tramite API REST
3. Il server centrale inoltra le richieste agli agenti MetaTrader appropriati
4. Gli agenti MetaTrader eseguono le operazioni sulle istanze locali e restituiscono i risultati
5. I risultati vengono aggregati dal server centrale e visualizzati nell'interfaccia web

## Configurazione Master-Slave
- Possibilità di designare uno o più account come "master"
- Configurazione di quali account "slave" seguono quali account "master"
- Impostazioni per ogni relazione master-slave:
  - Dimensione delle operazioni (fissa o proporzionale)
  - Direzione (stessa o opposta)
  - Opzioni per stop loss e take profit personalizzati

## Aggiunta di Nuovi Server/Gruppi
1. Installazione dell'agente MetaTrader sul nuovo server Windows
2. Configurazione dell'agente con le credenziali delle istanze MetaTrader
3. Registrazione del nuovo server nell'interfaccia web centrale
4. Configurazione delle relazioni master-slave se necessario

## Sicurezza
- Autenticazione per l'accesso all'interfaccia web
- Comunicazione sicura tra i componenti (HTTPS)
- Credenziali MetaTrader memorizzate in modo sicuro

## Vantaggi di questa Architettura
- **Semplicità**: Componenti ben definiti con responsabilità chiare
- **Scalabilità**: Facile aggiunta di nuovi server e istanze MetaTrader
- **Flessibilità**: Configurazione personalizzabile delle relazioni master-slave
- **Centralizzazione**: Gestione di tutte le istanze da un'unica interfaccia
- **Indipendenza**: Ogni agente può funzionare autonomamente in caso di problemi di connessione
