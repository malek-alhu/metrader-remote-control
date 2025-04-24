from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
import json
import os
import uuid
import logging

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte

# Configurazione dell'autenticazione
auth = HTTPBasicAuth()
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'password')

@auth.verify_password
def verify_password(username, password):
    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
        return username
    return None

# Percorso del file di configurazione
CONFIG_FILE = 'config.json'

# Struttura dati per memorizzare le informazioni sui server MetaTrader
servers = {}
master_slave_config = {}

# Carica la configurazione se esiste
def load_config():
    global servers, master_slave_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                servers = config.get('servers', {})
                master_slave_config = config.get('master_slave_config', {})
            logger.info(f"Configurazione caricata: {len(servers)} server trovati")
        except Exception as e:
            logger.error(f"Errore nel caricamento della configurazione: {e}")

# Salva la configurazione
def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'servers': servers,
                'master_slave_config': master_slave_config
            }, f, indent=4)
        logger.info("Configurazione salvata con successo")
    except Exception as e:
        logger.error(f"Errore nel salvataggio della configurazione: {e}")

# Rotta principale
@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "message": "MetaTrader Remote Control API",
        "version": "1.0.0"
    })

# API per registrare un nuovo server MetaTrader
@app.route('/api/servers', methods=['POST'])
@auth.login_required
def register_server():
    data = request.json
    if not data or not all(k in data for k in ['name', 'url']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    server_id = str(uuid.uuid4())
    servers[server_id] = {
        'id': server_id,
        'name': data['name'],
        'url': data['url'],
        'status': 'offline',
        'accounts': []
    }
    save_config()
    return jsonify({"id": server_id, "message": "Server registrato con successo"}), 201

# API per ottenere tutti i server
@app.route('/api/servers', methods=['GET'])
@auth.login_required
def get_servers():
    return jsonify(list(servers.values()))

# API per ottenere un server specifico
@app.route('/api/servers/<server_id>', methods=['GET'])
@auth.login_required
def get_server(server_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    return jsonify(servers[server_id])

# API per aggiornare un server
@app.route('/api/servers/<server_id>', methods=['PUT'])
@auth.login_required
def update_server(server_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "Dati mancanti"}), 400
    
    # Aggiorna solo i campi forniti
    for key, value in data.items():
        if key != 'id':  # Non permettere di modificare l'ID
            servers[server_id][key] = value
    
    save_config()
    return jsonify({"message": "Server aggiornato con successo"})

# API per eliminare un server
@app.route('/api/servers/<server_id>', methods=['DELETE'])
@auth.login_required
def delete_server(server_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    del servers[server_id]
    
    # Rimuovi anche le configurazioni master-slave associate
    for master_id in list(master_slave_config.keys()):
        if master_id == server_id:
            del master_slave_config[master_id]
        else:
            # Rimuovi questo server dalle configurazioni slave
            slaves = master_slave_config[master_id].get('slaves', [])
            master_slave_config[master_id]['slaves'] = [s for s in slaves if s['server_id'] != server_id]
    
    save_config()
    return jsonify({"message": "Server eliminato con successo"})

# API per registrare un account MetaTrader su un server
@app.route('/api/servers/<server_id>/accounts', methods=['POST'])
@auth.login_required
def register_account(server_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    data = request.json
    if not data or not all(k in data for k in ['account_number', 'description']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    account_id = str(uuid.uuid4())
    account = {
        'id': account_id,
        'account_number': data['account_number'],
        'description': data['description'],
        'status': 'offline',
        'balance': 0,
        'equity': 0,
        'positions': [],
        'history': []
    }
    
    if 'accounts' not in servers[server_id]:
        servers[server_id]['accounts'] = []
    
    servers[server_id]['accounts'].append(account)
    save_config()
    return jsonify({"id": account_id, "message": "Account registrato con successo"}), 201

# API per ottenere tutti gli account di un server
@app.route('/api/servers/<server_id>/accounts', methods=['GET'])
@auth.login_required
def get_accounts(server_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    return jsonify(servers[server_id].get('accounts', []))

# API per ottenere un account specifico
@app.route('/api/servers/<server_id>/accounts/<account_id>', methods=['GET'])
@auth.login_required
def get_account(server_id, account_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    for account in servers[server_id].get('accounts', []):
        if account['id'] == account_id:
            return jsonify(account)
    
    return jsonify({"error": "Account non trovato"}), 404

# API per aggiornare un account
@app.route('/api/servers/<server_id>/accounts/<account_id>', methods=['PUT'])
@auth.login_required
def update_account(server_id, account_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "Dati mancanti"}), 400
    
    for i, account in enumerate(servers[server_id].get('accounts', [])):
        if account['id'] == account_id:
            # Aggiorna solo i campi forniti
            for key, value in data.items():
                if key != 'id':  # Non permettere di modificare l'ID
                    servers[server_id]['accounts'][i][key] = value
            
            save_config()
            return jsonify({"message": "Account aggiornato con successo"})
    
    return jsonify({"error": "Account non trovato"}), 404

# API per eliminare un account
@app.route('/api/servers/<server_id>/accounts/<account_id>', methods=['DELETE'])
@auth.login_required
def delete_account(server_id, account_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    for i, account in enumerate(servers[server_id].get('accounts', [])):
        if account['id'] == account_id:
            del servers[server_id]['accounts'][i]
            
            # Rimuovi anche le configurazioni master-slave associate
            for master_id in list(master_slave_config.keys()):
                if master_id == account_id:
                    del master_slave_config[master_id]
                else:
                    # Rimuovi questo account dalle configurazioni slave
                    slaves = master_slave_config[master_id].get('slaves', [])
                    master_slave_config[master_id]['slaves'] = [
                        s for s in slaves if not (s['server_id'] == server_id and s['account_id'] == account_id)
                    ]
            
            save_config()
            return jsonify({"message": "Account eliminato con successo"})
    
    return jsonify({"error": "Account non trovato"}), 404

# API per configurare una relazione master-slave
@app.route('/api/master-slave', methods=['POST'])
@auth.login_required
def configure_master_slave():
    data = request.json
    if not data or not all(k in data for k in ['master_server_id', 'master_account_id', 'slaves']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    master_server_id = data['master_server_id']
    master_account_id = data['master_account_id']
    
    # Verifica che il master esista
    if master_server_id not in servers:
        return jsonify({"error": "Server master non trovato"}), 404
    
    master_exists = False
    for account in servers[master_server_id].get('accounts', []):
        if account['id'] == master_account_id:
            master_exists = True
            break
    
    if not master_exists:
        return jsonify({"error": "Account master non trovato"}), 404
    
    # Verifica che tutti gli slave esistano
    for slave in data['slaves']:
        if not all(k in slave for k in ['server_id', 'account_id', 'size_ratio', 'direction', 'use_sl_tp']):
            return jsonify({"error": "Dati slave incompleti"}), 400
        
        slave_server_id = slave['server_id']
        slave_account_id = slave['account_id']
        
        if slave_server_id not in servers:
            return jsonify({"error": f"Server slave {slave_server_id} non trovato"}), 404
        
        slave_exists = False
        for account in servers[slave_server_id].get('accounts', []):
            if account['id'] == slave_account_id:
                slave_exists = True
                break
        
        if not slave_exists:
            return jsonify({"error": f"Account slave {slave_account_id} non trovato"}), 404
    
    # Crea o aggiorna la configurazione master-slave
    master_key = f"{master_server_id}_{master_account_id}"
    master_slave_config[master_key] = {
        'master_server_id': master_server_id,
        'master_account_id': master_account_id,
        'slaves': data['slaves']
    }
    
    save_config()
    return jsonify({"message": "Configurazione master-slave salvata con successo"})

# API per ottenere tutte le configurazioni master-slave
@app.route('/api/master-slave', methods=['GET'])
@auth.login_required
def get_master_slave_configs():
    return jsonify(list(master_slave_config.values()))

# API per ottenere una configurazione master-slave specifica
@app.route('/api/master-slave/<master_server_id>/<master_account_id>', methods=['GET'])
@auth.login_required
def get_master_slave_config(master_server_id, master_account_id):
    master_key = f"{master_server_id}_{master_account_id}"
    if master_key not in master_slave_config:
        return jsonify({"error": "Configurazione master-slave non trovata"}), 404
    
    return jsonify(master_slave_config[master_key])

# API per eliminare una configurazione master-slave
@app.route('/api/master-slave/<master_server_id>/<master_account_id>', methods=['DELETE'])
@auth.login_required
def delete_master_slave_config(master_server_id, master_account_id):
    master_key = f"{master_server_id}_{master_account_id}"
    if master_key not in master_slave_config:
        return jsonify({"error": "Configurazione master-slave non trovata"}), 404
    
    del master_slave_config[master_key]
    save_config()
    return jsonify({"message": "Configurazione master-slave eliminata con successo"})

# API per aprire una posizione su un account (supporta ordini limite)
@app.route('/api/servers/<server_id>/accounts/<account_id>/positions', methods=['POST'])
@auth.login_required
def open_position(server_id, account_id):
    if server_id not in servers:
        return jsonify({"error": "Server non trovato"}), 404
    
    account_exists = False
    for account in servers[server_id].get('accounts', []):
        if account['id'] == account_id:
            account_exists = True
            break
    
    if not account_exists:
        return jsonify({"error": "Account non trovato"}), 404
    
    data = request.json
    if not data or not all(k in data for k in ['symbol', 'type', 'volume']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    # Verifica se è un ordine limite o market
    is_limit_order = 'limit_price' in data and data['limit_price'] is not None
    
    # Qui dovresti inviare la richiesta all'agente MetaTrader sul server specificato
    # Per ora, simuliamo una risposta di successo
    
    position_id = str(uuid.uuid4())
    response = {
        "id": position_id,
        "message": f"Richiesta di apertura posizione {'limite' if is_limit_order else 'market'} inviata",
        "details": {
            "server_id": server_id,
            "account_id": account_id,
            "symbol": data['symbol'],
            "type": data['type'],
            "volume": data['volume'],
            "sl": data.get('sl'),
            "tp": data.get('tp'),
            "is_limit_order": is_limit_order,
            "limit_price": data.get('limit_price')
        }
    }
    
    # Se questo è un account master, propaga l'operazione agli slave
    master_key = f"{server_id}_{account_id}"
    if master_key in master_slave_config:
        slaves = master_slave_config[master_key].get('slaves', [])
        slave_operations = []
        
        for slave in slaves:
            slave_server_id = slave['server_id']
            slave_account_id = slave['account_id']
            size_ratio = slave['size_ratio']
            direction = slave['direction']
            use_sl_tp = slave['use_sl_tp']
            
            # Calcola il volume per lo slave
            slave_volume = data['volume'] * size_ratio
            
            # Determina il tipo di operazione in base alla direzione
            slave_type = data['type']
            if direction == 'opposite':
                if slave_type == 'buy':
                    slave_type = 'sell'
                elif slave_type == 'sell':
                    slave_type = 'buy'
            
            # Prepara i parametri SL/TP se necessario
            slave_sl = data.get('sl') if use_sl_tp else None
            slave_tp = data.get('tp') if use_sl_tp else None
            
            # Determina se usare un ordine limite o market per lo slave
            # Se il master usa un ordine limite, lo slave proverà a usare un ordine limite
            # ma se non riesce, userà un ordine market come fallback
            slave_is_limit_order = is_limit_order
            slave_limit_price = data.get('limit_price')
            
            # Qui dovresti inviare la richiesta all'agente MetaTrader sul server dello slave
            # Per ora, simuliamo una risposta di successo
            
            slave_position_id = str(uuid.uuid4())
            slave_operation = {
                "id": slave_position_id,
                "server_id": slave_server_id,
                "account_id": slave_account_id,
                "symbol": data['symbol'],
                "type": slave_type,
                "volume": slave_volume,
                "sl": slave_sl,
                "tp": slave_tp,
                "is_limit_order": slave_is_limit_order,
                "limit_price": slave_limit_price,
                "fallback_to_market": True  # Indica che lo slave deve usare un ordine market come fallback
            }
            
            slave_operations.append(slave_operation)
        
        response["slave_operations"] = slave_operations
    
    return jsonify(response)

# API per chiudere una posizione su un account
@app.route('/api/servers/<server_id>/accounts/<account_id>/pos
(Content truncated due to size limit. Use line ranges to read in chunks)