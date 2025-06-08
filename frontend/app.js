// API endpoints
const API_BASE_URL = 'http://127.0.0.1:8000';
const API = {
    login: `${API_BASE_URL}/login`,
    autocomplete: `${API_BASE_URL}/autocomplete/person`,
    person: `${API_BASE_URL}/person`,
    createTransfer: `${API_BASE_URL}/transfer/create`,
    approveTransfer: `${API_BASE_URL}/transfer/approve`,
    getTransfers: `${API_BASE_URL}/transfers`
};

// DOM Elements
const elements = {
    loginSection: document.getElementById('loginSection'),
    appSection: document.getElementById('appSection'),
    loginForm: document.getElementById('loginForm'),
    userEmail: document.getElementById('userEmail'),
    userBalance: document.getElementById('userBalance'),
    logoutBtn: document.getElementById('logoutBtn'),
    searchInput: document.getElementById('searchInput'),
    autocompleteDropdown: document.getElementById('autocompleteDropdown'),
    personDetails: document.getElementById('personDetails'),
    detailFirstName: document.getElementById('detailFirstName'),
    detailLastName: document.getElementById('detailLastName'),
    detailEmail: document.getElementById('detailEmail'),
    detailPhone: document.getElementById('detailPhone'),
    transferAmount: document.getElementById('transferAmount'),
    transferBtn: document.getElementById('transferBtn'),
    transfersList: document.getElementById('transfersList')
};

// State
let currentUser = null;
let searchTimeout = null;
let selectedPerson = null;

// Event Listeners
elements.loginForm.addEventListener('submit', handleLogin);
elements.logoutBtn.addEventListener('click', handleLogout);
elements.searchInput.addEventListener('input', handleSearchInput);
elements.transferBtn.addEventListener('click', handleTransfer);

// Login Handler
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(API.login, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const userData = await response.json();
        currentUser = userData;
        elements.userEmail.textContent = `${userData.first_name} ${userData.last_name}`;
        elements.userBalance.textContent = userData.balance?.toFixed(2) || '0.00';
        elements.loginSection.classList.add('hidden');
        elements.appSection.classList.remove('hidden');
        
        // Load transfers after login
        loadTransfers();
    } catch (error) {
        console.error('Login error:', error);
        alert('Invalid credentials. Please try again.');
    }
}

// Transfer Handler
async function handleTransfer() {
    if (!selectedPerson || !currentUser) {
        alert('Please select a recipient first');
        return;
    }

    const amount = parseFloat(elements.transferAmount.value);
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    try {
        const response = await fetch(API.createTransfer, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                from_email: currentUser.email,
                to_email: selectedPerson.email,
                amount: amount
            })
        });

        if (!response.ok) {
            throw new Error('Failed to create transfer');
        }

        const result = await response.json();
        alert('Transfer request created successfully');
        elements.transferAmount.value = '';
        
        // Reload transfers
        loadTransfers();
    } catch (error) {
        console.error('Transfer error:', error);
        alert('Failed to create transfer. Please try again.');
    }
}

// Approve Transfer Handler
async function handleApproveTransfer(transferId) {
    try {
        const response = await fetch(API.approveTransfer, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transfer_id: transferId,
                to_email: currentUser.email
            })
        });

        if (!response.ok) {
            throw new Error('Failed to approve transfer');
        }

        const result = await response.json();
        alert('Transfer approved successfully');
        
        // Reload transfers and update balance
        loadTransfers();
        updateUserBalance();
    } catch (error) {
        console.error('Approve transfer error:', error);
        alert('Failed to approve transfer. Please try again.');
    }
}

// Load Transfers
async function loadTransfers() {
    if (!currentUser) return;

    try {
        const response = await fetch(`${API.getTransfers}/${currentUser.email}`);
        if (!response.ok) {
            throw new Error('Failed to load transfers');
        }

        const transfers = await response.json();
        displayTransfers(transfers);
    } catch (error) {
        console.error('Load transfers error:', error);
    }
}

// Display Transfers
function displayTransfers(transfers) {
    elements.transfersList.innerHTML = '';
    
    transfers.forEach(transfer => {
        const isIncoming = transfer.to_email === currentUser.email;
        const otherParty = isIncoming ? transfer.from_email : transfer.to_email;
        
        const transferEl = document.createElement('div');
        transferEl.className = `transfer-item ${transfer.status}`;
        transferEl.innerHTML = `
            <div class="transfer-header">
                <span class="transfer-amount">$${transfer.amount.toFixed(2)}</span>
                <span class="transfer-status ${transfer.status}">${transfer.status}</span>
            </div>
            <div>${isIncoming ? 'From' : 'To'}: ${otherParty}</div>
            <div class="transfer-timestamp">
                Created: ${new Date(transfer.created_at).toLocaleString()}
            </div>
            ${transfer.status === 'pending' && isIncoming ? `
                <div class="transfer-actions">
                    <button onclick="handleApproveTransfer('${transfer._id}')" class="btn">
                        Approve Transfer
                    </button>
                </div>
            ` : ''}
        `;
        
        elements.transfersList.appendChild(transferEl);
    });
}

// Update User Balance
async function updateUserBalance() {
    try {
        const response = await fetch(`${API.person}?email=${currentUser.email}`);
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        currentUser = userData;
        elements.userBalance.textContent = userData.balance?.toFixed(2) || '0.00';
    } catch (error) {
        console.error('Update balance error:', error);
    }
}

// Display Person Details
function displayPersonDetails(person) {
    selectedPerson = person;
    elements.detailFirstName.textContent = person.first_name;
    elements.detailLastName.textContent = person.last_name;
    elements.detailEmail.textContent = person.email;
    elements.detailPhone.textContent = person.phone;
    elements.personDetails.classList.remove('hidden');
}

// Logout Handler
function handleLogout() {
    currentUser = null;
    elements.loginForm.reset();
    elements.loginSection.classList.remove('hidden');
    elements.appSection.classList.add('hidden');
    elements.personDetails.classList.add('hidden');
    elements.autocompleteDropdown.classList.add('hidden');
    elements.searchInput.value = '';
}

// Search Input Handler
function handleSearchInput(e) {
    const query = e.target.value;
    
    // Clear previous timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    // Hide dropdown if input is empty
    if (!query.trim()) {
        elements.autocompleteDropdown.classList.add('hidden');
        return;
    }

    // Debounce API call
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API.autocomplete}?query=${query}`);
            const results = await response.json();

            if (results && results.length > 0) {
                displayAutocompleteResults(results);
            } else {
                elements.autocompleteDropdown.classList.add('hidden');
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
        }
    }, 300);
}

// Display Autocomplete Results
function displayAutocompleteResults(results) {
    elements.autocompleteDropdown.innerHTML = '';
    
    results.forEach(person => {
        const div = document.createElement('div');
        div.className = 'dropdown-item';
        div.textContent = `${person.first_name} ${person.last_name}    ${person.email}`;
        div.addEventListener('click', async () => {
            try {
                const response = await fetch(`${API.person}?email=${person.email}`);
                const personDetails = await response.json();
                if (personDetails) {
                    displayPersonDetails(personDetails);
                    elements.searchInput.value = `${person.first_name} ${person.last_name}`;
                }
            } catch (error) {
                console.error('Error fetching person details:', error);
            }
            elements.autocompleteDropdown.classList.add('hidden');
        });
        elements.autocompleteDropdown.appendChild(div);
    });

    elements.autocompleteDropdown.classList.remove('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!elements.searchInput.contains(e.target) && !elements.autocompleteDropdown.contains(e.target)) {
        elements.autocompleteDropdown.classList.add('hidden');
    }
}); 