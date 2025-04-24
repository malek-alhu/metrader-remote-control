// Configurazione globale
let config = {
    apiUrl: 'http://localhost:5000',
    refreshInterval: 5000
};

// Dati globali
let servers = [];
let masterSlaveConfigs = [];

// Elementi DOM
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav-link');

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    // Carica le impostazioni salvate
    loadSettings();
    
    // Inizializza la navigazione
    initNavigation();
    
    // Inizializza i gestori degli eventi
    initEventHandlers();
    
    // Carica i dati iniziali
    loadInitialData();
    
    // Imposta l'aggiornamento periodico
    setInterval(refreshData, config.refreshInterval);
});

// Funzione per caricare le impostazioni
function loadSettings() {
    const savedApiUrl = localStorage.getItem('apiUrl');
    const savedRefreshInterval = localStorage.getItem('refreshInterval');
    
    if (savedApiUrl) {
        config.apiUrl = savedApiUrl;
        document.getElementById('api-url').value = savedApiUrl;
    }
    
    if (savedRefreshInterval) {
        config.refreshInterval = parseInt(savedRefreshInterval) * 1000;
        document.getElementById('refresh-interval').value = parseInt(savedRefreshInterval);
    }
}

// Funzione per salvare le impostazioni
function saveSettings() {
    const apiUrl = document.getElementById('api-url').value;
    const refreshInterval = document.getElementById('refresh-interval').value;
    
    localStorage.setItem('apiUrl', apiUrl);
    localStorage.setItem('refreshInterval', refreshInterval);
    
    config.apiUrl = apiUrl;
    config.refreshInterval = parseInt(refreshInterval) * 1000;
    
    alert('Impostazioni salvate con successo');
}

// Funzione per inizializzare la navigazione
function initNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Rimuovi la classe active da tutti i link
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Aggiungi la classe active al link cliccato
            link.classList.add('active');
            
            // Ottieni l'ID della sezione da mostrare
            const targetId = link.getAttribute('href').substring(1);
            
            // Nascondi tutte le sezioni
            sections.forEach(section => {
                section.classList.add('d-none');
                section.classList.remove('active');
            });
            
            // Mostra la sezione target
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.remove('d-none');
                targetSection.classList.add('active');
            }
        });
    });
}

// Funzione per inizializzare i gestori degli eventi
function initEventHandlers() {
    // Form delle impostazioni
    document.getElementById('settings-form').addEventListener('submit', (e) => {
        e.preventDefault();
        saveSettings();
    });
    
    // Pulsante per aggiungere un server
    document.getElementById('add-server-btn').addEventListener('click', () => {
        addServer();
    });
    
    // Pulsante per aggiungere un account
    document.getElementById('add-account-btn').addEventListener('click', () => {
        addAccount();
    });
    
    // Pulsante per aggiungere uno slave
    document.getElementById('add-slave-btn').addEventListener('click', () => {
        addSlaveRow();
    });
    
    // Pulsante per aggiungere una configurazione master-slave
    document.getElementById('add-master-slave-btn').addEventListener('click', () => {
        addMasterSlaveConfig();
    });
    
    // Pulsante per aprire una posizione
    document.getElementById('open-position-btn').addEventListener('click', () => {
        openPosition();
    });
    
    // Pulsante per aprire il modale di apertura posizione
    document.getElementById('open-position-modal-btn').addEventListener('click', () => {
        const serverId = document.getElementById('open-position-modal-btn').getAttribute('data-server-id');
        const accountId = document.getElementById('open-position-modal-btn').getAttribute('data-account-id');
        
        document.getElementById('position-server-id').value = serverId;
        document.getElementById('position-account-id').value = accountId;
        
        const modal = new bootstrap.Modal(document.getElementById('openPositionModal'));
        modal.show();
    });
    
    // Pulsante per chiudere tutte le posizioni
    document.getElementById('close-all-positions-btn').addEventListener('click', () => {
        closeAllPositions();
    });
    
    // Gestione del cambio di server nel form di aggiunta account
    document.getElementById('account-server').addEventListener('change', () => {
        // In una implementazione reale, qui si potrebbe caricare la lista degli account disponibili sul server selezionato
    });
    
    // Gestione del cambio di server master nel form di configurazione master-slave
    document.getElementById('master-server').addEventListener('change', () => {
        loadMasterAccounts();
    });
}

// Funzione per caricare i dati iniziali
function loadInitialData() {
    // Carica i server
    loadServers();
    
    // Carica le configurazioni master-slave
    loadMasterSlaveConfigs();
}

// Funzione per aggiornare i dati periodicamente
function refreshData() {
    // Aggiorna i server
    loadServers();
    
    // Aggiorna le configurazioni master-slave
    loadMasterSlaveConfigs();
}

// Funzione per caricare i server
function loadServers() {
    axios.get(`${config.apiUrl}/api/servers`)
        .then(response => {
            servers = response.data;
            
            // Aggiorna i contatori
            updateCounters();
            
            // Aggiorna la tabella dello stato dei server
            updateServerStatusTable();
            
            // Aggiorna i container delle card dei server
            updateServerCards();
            
            // Aggiorna i container delle card degli account
            updateAccountCards();
            
            // Aggiorna le select dei server nei form
            updateServerSelects();
        })
        .catch(error => {
            console.error('Errore nel caricamento dei server:', error);
        });
}

// Funzione per caricare le configurazioni master-slave
function loadMasterSlaveConfigs() {
    axios.get(`${config.apiUrl}/api/master-slave`)
        .then(response => {
            masterSlaveConfigs = response.data;
            
            // Aggiorna i contatori
            updateCounters();
            
            // Aggiorna il container delle configurazioni master-slave
            updateMasterSlaveConfigsContainer();
        })
        .catch(error => {
            console.error('Errore nel caricamento delle configurazioni master-slave:', error);
        });
}

// Funzione per aggiornare i contatori
function updateCounters() {
    // Conta i server
    document.getElementById('total-servers').textContent = servers.length;
    
    // Conta gli account
    let accountCount = 0;
    servers.forEach(server => {
        accountCount += server.accounts ? server.accounts.length : 0;
    });
    document.getElementById('total-accounts').textContent = accountCount;
    
    // Conta le posizioni
    let positionCount = 0;
    servers.forEach(server => {
        if (server.accounts) {
            server.accounts.forEach(account => {
                positionCount += account.positions ? account.positions.length : 0;
            });
        }
    });
    document.getElementById('total-positions').textContent = positionCount;
    
    // Conta le configurazioni master-slave
    document.getElementById('total-ms-configs').textContent = masterSlaveConfigs.length;
}

// Funzione per aggiornare la tabella dello stato dei server
function updateServerStatusTable() {
    const tableBody = document.getElementById('server-status-table');
    tableBody.innerHTML = '';
    
    servers.forEach(server => {
        const row = document.createElement('tr');
        
        const nameCell = document.createElement('td');
        nameCell.textContent = server.name;
        row.appendChild(nameCell);
        
        const urlCell = document.createElement('td');
        urlCell.textContent = server.url;
        row.appendChild(urlCell);
        
        const statusCell = document.createElement('td');
        const statusIndicator = document.createElement('span');
        statusIndicator.classList.add('status-indicator');
        statusIndicator.classList.add(server.status === 'online' ? 'status-online' : 'status-offline');
        statusCell.appendChild(statusIndicator);
        statusCell.appendChild(document.createTextNode(server.status === 'online' ? 'Online' : 'Offline'));
        row.appendChild(statusCell);
        
        const accountsCell = document.createElement('td');
        accountsCell.textContent = server.accounts ? server.accounts.length : 0;
        row.appendChild(accountsCell);
        
        const actionsCell = document.createElement('td');
        
        const viewBtn = document.createElement('button');
        viewBtn.classList.add('btn', 'btn-sm', 'btn-info', 'me-2');
        viewBtn.innerHTML = '<i class="bi bi-eye"></i>';
        viewBtn.title = 'Visualizza';
        viewBtn.addEventListener('click', () => {
            // Implementa la visualizzazione dettagliata del server
        });
        actionsCell.appendChild(viewBtn);
        
        const editBtn = document.createElement('button');
        editBtn.classList.add('btn', 'btn-sm', 'btn-warning', 'me-2');
        editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
        editBtn.title = 'Modifica';
        editBtn.addEventListener('click', () => {
            // Implementa la modifica del server
        });
        actionsCell.appendChild(editBtn);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('btn', 'btn-sm', 'btn-danger');
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        deleteBtn.title = 'Elimina';
        deleteBtn.addEventListener('click', () => {
            deleteServer(server.id);
        });
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Funzione per aggiornare le card dei server
function updateServerCards() {
    const container = document.getElementById('server-cards-container');
    container.innerHTML = '';
    
    servers.forEach(server => {
        const col = document.createElement('div');
        col.classList.add('col-md-4', 'mb-4');
        
        const card = document.createElement('div');
        card.classList.add('card');
        
        const cardHeader = document.createElement('div');
        cardHeader.classList.add('card-header', 'd-flex', 'justify-content-between', 'align-items-center');
        
        const serverName = document.createElement('h5');
        serverName.classList.add('mb-0');
        serverName.textContent = server.name;
        
        const statusBadge = document.createElement('span');
        statusBadge.classList.add('badge', server.status === 'online' ? 'bg-success' : 'bg-danger');
        statusBadge.textContent = server.status === 'online' ? 'Online' : 'Offline';
        
        cardHeader.appendChild(serverName);
        cardHeader.appendChild(statusBadge);
        
        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body');
        
        const urlParagraph = document.createElement('p');
        urlParagraph.innerHTML = `<strong>URL:</strong> ${server.url}`;
        
        const accountsParagraph = document.createElement('p');
        accountsParagraph.innerHTML = `<strong>Account:</strong> ${server.accounts ? server.accounts.length : 0}`;
        
        cardBody.appendChild(urlParagraph);
        cardBody.appendChild(accountsParagraph);
        
        const cardFooter = document.createElement('div');
        cardFooter.classList.add('card-footer', 'd-flex', 'justify-content-between');
        
        const addAccountBtn = document.createElement('button');
        addAccountBtn.classList.add('btn', 'btn-sm', 'btn-primary');
        addAccountBtn.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Aggiungi Account';
        addAccountBtn.addEventListener('click', () => {
            document.getElementById('account-server').value = server.id;
            const modal = new bootstrap.Modal(document.getElementById('addAccountModal'));
            modal.show();
        });
        
        const deleteServerBtn = document.createElement('button');
        deleteServerBtn.classList.add('btn', 'btn-sm', 'btn-danger');
        deleteServerBtn.innerHTML = '<i class="bi bi-trash me-2"></i>Elimina Server';
        deleteServerBtn.addEventListener('click', () => {
            deleteServer(server.id);
        });
        
        cardFooter.appendChild(addAccountBtn);
        cardFooter.appendChild(deleteServerBtn);
        
        card.appendChild(cardHeader);
        card.appendChild(cardBody);
        card.appendChild(cardFooter);
        
        col.appendChild(card);
        container.appendChild(col);
    });
}

// Funzione per aggiornare le card degli account
function updateAccountCards() {
    const container = document.getElementById('account-cards-container');
    container.innerHTML = '';
    
    servers.forEach(server => {
        if (server.accounts && server.accounts.length > 0) {
            server.accounts.forEach(account => {
                const col = document.createElement('div');
                col.classList.add('col-md-4', 'mb-4');
                
                const card = document.createElement('div');
                card.classList.add('card', 'account-card');
                card.addEventListener('click', () => {
                    showAccountDetails(server.id, account.id);
                });
                
                const cardHeader = document.createElement('div');
                cardHeader.classList.add('card-header', 'd-flex', 'justify-content-between', 'align-items-center');
                
                const accountNumber = document.createElement('h5');
                accountNumber.classList.add('mb-0');
                accountNumber.textContent = account.description || `Account ${account.account_number}`;
                
                const statusBadge = document.createElement('span');
                statusBadge.classList.add('badge', account.status === 'online' ? 'bg-success' : 'bg-danger');
                statusBadge.textContent = account.status === 'online' ? 'Online' : 'Offline';
                
                cardHeader.appendChild(accountNumber);
                cardHeader.appendChild(statusBadge);
                
                const cardBody = document.createElement('div');
                cardBody.classList.add('card-body');
                
                const serverParagraph = document.createElement('p');
                serverParagraph.innerHTML = `<strong>Server:</strong> ${server.name}`;
                
                const balanceParagraph = document.createElement('p');
                balanceParagraph.innerHTML = `<strong>Saldo:</strong> ${account.balance || 0}`;
                
                const equityParagraph = document.createElement('p');
                equityParagraph.innerHTML = `<strong>Equity:</strong> ${account.equity || 0}`;
                
                const positionsParagraph = document.createElement('p');
                positionsParagraph.innerHTML = `<strong>Posizioni:</strong> ${account.positions ? account.positions.length : 0}`;
                
                cardBody.appendChild(serverParagraph);
                cardBody.appendChild(balanc
(Content truncated due to size limit. Use line ranges to read in chunks)