from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging
import os

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configurazione dell'agente
MT5_PATH = os.environ.get('MT5_PATH', "C:\\Program Files\\MetaTrader 5\\terminal64.exe")
CONFIG_FILE = 'agent_config.json'

# Carica la configurazione se esiste
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Errore nel caricamento della configurazione: {e}")
        return {
            'mt5_path': MT5_PATH,
            'accounts': []
        }

# Salva la configurazione
def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configurazione salvata con successo")
    except Exception as e:
        logger.error(f"Errore nel salvataggio della configurazione: {e}")

# Inizializza MetaTrader 5
def initialize_mt5(account_number, password, server):
    try:
        import MetaTrader5 as mt5
        
        # Chiudi eventuali istanze aperte
        mt5.shutdown()
        
        # Inizializza con i parametri specificati
        if not mt5.initialize(login=account_number, password=password, server=server, path=config['mt5_path']):
            logger.error(f"Inizializzazione MT5 fallita: {mt5.last_error()}")
            return False, f"Errore: {mt5.last_error()}"
        
        logger.info(f"MT5 inizializzato con successo per l'account {account_number}")
        return True, "Inizializzazione riuscita"
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione di MT5: {e}")
        return False, f"Errore: {e}"

# Ottieni informazioni sull'account
def get_account_info():
    try:
        import MetaTrader5 as mt5
        
        if not mt5.terminal_info():
            return False, "MT5 non inizializzato", None
        
        account_info = mt5.account_info()
        if account_info is None:
            return False, f"Errore nel recupero delle informazioni dell'account: {mt5.last_error()}", None
        
        # Converti l'oggetto namedtuple in dizionario
        account_info_dict = {
            'login': account_info.login,
            'server': account_info.server,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'currency': account_info.currency
        }
        
        return True, "Informazioni account recuperate con successo", account_info_dict
    except Exception as e:
        logger.error(f"Errore durante il recupero delle informazioni dell'account: {e}")
        return False, f"Errore: {e}", None

# Ottieni posizioni aperte
def get_positions():
    try:
        import MetaTrader5 as mt5
        
        if not mt5.terminal_info():
            return False, "MT5 non inizializzato", None
        
        positions = mt5.positions_get()
        if positions is None:
            return False, f"Errore nel recupero delle posizioni: {mt5.last_error()}", None
        
        # Converti gli oggetti namedtuple in dizionari
        positions_list = []
        for position in positions:
            position_dict = {
                'ticket': position.ticket,
                'time': position.time,
                'type': position.type,
                'magic': position.magic,
                'symbol': position.symbol,
                'volume': position.volume,
                'price_open': position.price_open,
                'price_current': position.price_current,
                'sl': position.sl,
                'tp': position.tp,
                'profit': position.profit
            }
            positions_list.append(position_dict)
        
        return True, "Posizioni recuperate con successo", positions_list
    except Exception as e:
        logger.error(f"Errore durante il recupero delle posizioni: {e}")
        return False, f"Errore: {e}", None

# Ottieni cronologia delle operazioni
def get_history(days=7):
    try:
        import MetaTrader5 as mt5
        from datetime import datetime, timedelta
        
        if not mt5.terminal_info():
            return False, "MT5 non inizializzato", None
        
        # Calcola l'intervallo di tempo
        now = datetime.now()
        from_date = now - timedelta(days=days)
        
        # Ottieni la cronologia
        history = mt5.history_deals_get(from_date, now)
        if history is None:
            return False, f"Errore nel recupero della cronologia: {mt5.last_error()}", None
        
        # Converti gli oggetti namedtuple in dizionari
        history_list = []
        for deal in history:
            deal_dict = {
                'ticket': deal.ticket,
                'time': deal.time,
                'type': deal.type,
                'entry': deal.entry,
                'magic': deal.magic,
                'symbol': deal.symbol,
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'commission': deal.commission,
                'swap': deal.swap,
                'fee': deal.fee
            }
            history_list.append(deal_dict)
        
        return True, "Cronologia recuperata con successo", history_list
    except Exception as e:
        logger.error(f"Errore durante il recupero della cronologia: {e}")
        return False, f"Errore: {e}", None

# Apri una posizione (market o limite)
def open_position(symbol, order_type, volume, sl=0.0, tp=0.0, limit_price=None, fallback_to_market=False):
    try:
        import MetaTrader5 as mt5
        
        if not mt5.terminal_info():
            return False, "MT5 non inizializzato", None
        
        # Mappa il tipo di ordine
        if order_type.lower() == 'buy':
            mt5_order_type = mt5.ORDER_TYPE_BUY if limit_price is None else mt5.ORDER_TYPE_BUY_LIMIT
        elif order_type.lower() == 'sell':
            mt5_order_type = mt5.ORDER_TYPE_SELL if limit_price is None else mt5.ORDER_TYPE_SELL_LIMIT
        else:
            return False, f"Tipo di ordine non valido: {order_type}", None
        
        # Ottieni il prezzo corrente
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False, f"Simbolo non trovato: {symbol}", None
        
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
        
        # Prepara la richiesta
        if limit_price is None:
            # Ordine market
            price = mt5.symbol_info_tick(symbol).ask if mt5_order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": mt5_order_type,
                "price": price,
                "sl": float(sl) if sl else 0.0,
                "tp": float(tp) if tp else 0.0,
                "deviation": 10,
                "magic": 234000,
                "comment": "Aperto da MetaTrader Remote Control",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        else:
            # Ordine limite
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": float(volume),
                "type": mt5_order_type,
                "price": float(limit_price),
                "sl": float(sl) if sl else 0.0,
                "tp": float(tp) if tp else 0.0,
                "deviation": 10,
                "magic": 234000,
                "comment": "Ordine limite aperto da MetaTrader Remote Control",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        
        # Invia l'ordine
        result = mt5.order_send(request)
        
        # Se l'ordine limite fallisce e fallback_to_market è True, prova con un ordine market
        if result.retcode != mt5.TRADE_RETCODE_DONE and limit_price is not None and fallback_to_market:
            logger.info(f"Ordine limite fallito, tentativo con ordine market: {result.retcode}")
            
            # Converti in ordine market
            if order_type.lower() == 'buy':
                mt5_order_type = mt5.ORDER_TYPE_BUY
            else:
                mt5_order_type = mt5.ORDER_TYPE_SELL
            
            price = mt5.symbol_info_tick(symbol).ask if mt5_order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": mt5_order_type,
                "price": price,
                "sl": float(sl) if sl else 0.0,
                "tp": float(tp) if tp else 0.0,
                "deviation": 10,
                "magic": 234000,
                "comment": "Fallback a ordine market da MetaTrader Remote Control",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return False, f"Errore nell'apertura della posizione: {result.retcode}", None
        
        # Converti il risultato in dizionario
        result_dict = {
            'retcode': result.retcode,
            'deal': result.deal,
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'bid': result.bid,
            'ask': result.ask,
            'comment': result.comment,
            'request': request,
            'is_market_fallback': limit_price is not None and fallback_to_market and result.retcode == mt5.TRADE_RETCODE_DONE
        }
        
        return True, "Posizione aperta con successo", result_dict
    except Exception as e:
        logger.error(f"Errore durante l'apertura della posizione: {e}")
        return False, f"Errore: {e}", None

# Chiudi una posizione
def close_position(position_id):
    try:
        import MetaTrader5 as mt5
        
        if not mt5.terminal_info():
            return False, "MT5 non inizializzato", None
        
        # Ottieni la posizione
        position = mt5.positions_get(ticket=position_id)
        if position is None or len(position) == 0:
            return False, f"Posizione non trovata: {position_id}", None
        
        position = position[0]
        
        # Determina il tipo di ordine per la chiusura
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        # Ottieni il prezzo corrente
        price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask
        
        # Prepara la richiesta
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": position.ticket,
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": "Chiuso da MetaTrader Remote Control",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Invia l'ordine
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return False, f"Errore nella chiusura della posizione: {result.retcode}", None
        
        # Converti il risultato in dizionario
        result_dict = {
            'retcode': result.retcode,
            'deal': result.deal,
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'bid': result.bid,
            'ask': result.ask,
            'comment': result.comment,
            'request': request
        }
        
        return True, "Posizione chiusa con successo", result_dict
    except Exception as e:
        logger.error(f"Errore durante la chiusura della posizione: {e}")
        return False, f"Errore: {e}", None

# Rotta principale
@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "message": "MetaTrader Remote Control Agent",
        "version": "1.0.0"
    })

# API per inizializzare MetaTrader 5
@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    data = request.json
    if not data or not all(k in data for k in ['account_number', 'password', 'server']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    success, message = initialize_mt5(data['account_number'], data['password'], data['server'])
    
    if success:
        # Aggiorna la configurazione
        config = load_config()
        
        # Verifica se l'account esiste già
        account_exists = False
        for i, account in enumerate(config.get('accounts', [])):
            if account['account_number'] == data['account_number']:
                account_exists = True
                config['accounts'][i] = {
                    'account_number': data['account_number'],
                    'server': data['server'],
                    'description': data.get('description', f"Account {data['account_number']}")
                }
                break
        
        if not account_exists:
            if 'accounts' not in config:
                config['accounts'] = []
            
            config['accounts'].append({
                'account_number': data['account_number'],
                'server': data['server'],
                'description': data.get('description', f"Account {data['account_number']}")
            })
        
        save_config(config)
        
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 500

# API per ottenere informazioni sull'account
@app.route('/api/account', methods=['GET'])
def api_account():
    success, message, data = get_account_info()
    
    if success:
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "message": message}), 500

# API per ottenere posizioni aperte
@app.route('/api/positions', methods=['GET'])
def api_positions():
    success, message, data = get_positions()
    
    if success:
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "message": message}), 500

# API per ottenere cronologia delle operazioni
@app.route('/api/history', methods=['GET'])
def api_history():
    days = request.args.get('days', default=7, type=int)
    success, message, data = get_history(days)
    
    if success:
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "message": message}), 500

# API per aprire una posizione (market o limite)
@app.route('/api/positions', methods=['POST'])
def api_open_position():
    data = request.json
    if not data or not all(k in data for k in ['symbol', 'type', 'volume']):
        return jsonify({"error": "Dati mancanti"}), 400
    
    # Verifica se è un ordine limite
    limit_price = data.get('limit_price')
    fallback_to_market = data.get('fallback_to_market', False)
    
    success, message, result = open_position(
        data['symbol'],
        data['type'],
        data['volume'],
        data.get('sl', 0.0),
        da
(Content truncated due to size limit. Use line ranges to read in chunks)