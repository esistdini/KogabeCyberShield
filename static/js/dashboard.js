// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize contacts data table
    initializeContactsTable();
    
    // Setup charts
    initializeCharts();
    
    // Fetch contact data periodically
    fetchContactsPeriodically();
});

// Initialize the contacts data table
function initializeContactsTable() {
    fetchContacts()
        .then(contacts => {
            renderContactsTable(contacts);
        })
        .catch(error => {
            console.error('Error fetching contacts:', error);
            showErrorMessage('Failed to load contacts. Please try again later.');
        });
}

// Fetch contacts from API
async function fetchContacts() {
    const response = await fetch('/api/contacts');
    if (!response.ok) {
        throw new Error('Failed to fetch contacts');
    }
    return await response.json();
}

// Render the contacts table
function renderContactsTable(contacts) {
    const tableBody = document.getElementById('contacts-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (contacts.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                No contact submissions yet
            </td>
        `;
        tableBody.appendChild(emptyRow);
        return;
    }
    
    contacts.forEach(contact => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-800 transition-colors';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">${contact.name}</td>
            <td class="px-6 py-4 whitespace-nowrap">${contact.email}</td>
            <td class="px-6 py-4 whitespace-nowrap">${contact.phone || 'N/A'}</td>
            <td class="px-6 py-4">
                <div class="truncate max-w-xs" title="${contact.message}">
                    ${contact.message}
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">${contact.created_at}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex space-x-3">
                    <button 
                        class="text-indigo-400 hover:text-indigo-300 view-details"
                        data-id="${contact.id}"
                    >
                        View Details
                    </button>
                    <button 
                        class="text-red-400 hover:text-red-300 delete-contact"
                        data-id="${contact.id}"
                    >
                        Delete
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Add event listeners for view details buttons
    document.querySelectorAll('.view-details').forEach(button => {
        button.addEventListener('click', function() {
            const contactId = this.getAttribute('data-id');
            const contact = contacts.find(c => c.id == contactId);
            if (contact) {
                showContactDetails(contact);
            }
        });
    });
    
    // Add event listeners for delete buttons
    document.querySelectorAll('.delete-contact').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this contact?')) {
                const contactId = this.getAttribute('data-id');
                deleteContact(contactId);
            }
        });
    });
    
    // Update dashboard stats
    updateDashboardStats(contacts);
}

// Show contact details modal
function showContactDetails(contact) {
    const modal = document.getElementById('contact-modal');
    const overlay = document.getElementById('modal-overlay');
    const modalContent = document.getElementById('modal-content');
    
    if (modal && overlay && modalContent) {
        modalContent.innerHTML = `
            <h3 class="text-xl font-bold mb-4">Contact from ${contact.name}</h3>
            <div class="mb-4">
                <p class="text-gray-400">Email:</p>
                <p class="font-medium">${contact.email}</p>
            </div>
            <div class="mb-4">
                <p class="text-gray-400">Phone:</p>
                <p class="font-medium">${contact.phone || 'Not provided'}</p>
            </div>
            <div class="mb-4">
                <p class="text-gray-400">Submitted on:</p>
                <p class="font-medium">${contact.created_at}</p>
            </div>
            <div class="mb-6">
                <p class="text-gray-400">Message:</p>
                <p class="font-medium whitespace-pre-wrap">${contact.message}</p>
            </div>
            <div class="flex justify-end">
                <button id="close-modal" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md">
                    Close
                </button>
            </div>
        `;
        
        modal.classList.remove('hidden');
        overlay.classList.remove('hidden');
        
        // Close modal event
        document.getElementById('close-modal').addEventListener('click', function() {
            modal.classList.add('hidden');
            overlay.classList.add('hidden');
        });
        
        // Close on overlay click
        overlay.addEventListener('click', function() {
            modal.classList.add('hidden');
            overlay.classList.add('hidden');
        });
    }
}

// Show error message
function showErrorMessage(message) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorContainer.classList.add('hidden');
        }, 5000);
    }
}

// Update dashboard statistics
function updateDashboardStats(contacts) {
    // Total contacts
    const totalContacts = document.getElementById('total-contacts');
    if (totalContacts) {
        totalContacts.textContent = contacts.length;
    }
    
    // Recent contacts (last 7 days)
    const recentContacts = document.getElementById('recent-contacts');
    if (recentContacts) {
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        
        const recentCount = contacts.filter(contact => {
            const contactDate = new Date(contact.created_at);
            return contactDate >= sevenDaysAgo;
        }).length;
        
        recentContacts.textContent = recentCount;
    }
}

// Initialize dashboard charts
function initializeCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded');
        return;
    }
    
    // Contact trend chart
    fetchContacts().then(contacts => {
        createContactTrendChart(contacts);
    });
}

// Create contact trend chart
function createContactTrendChart(contacts) {
    const ctx = document.getElementById('contact-trend-chart');
    if (!ctx) return;
    
    // Process data - last 30 days
    const dates = {};
    const now = new Date();
    for (let i = 0; i < 30; i++) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateString = date.toISOString().split('T')[0];
        dates[dateString] = 0;
    }
    
    // Count contacts by date
    contacts.forEach(contact => {
        const contactDate = contact.created_at.split(' ')[0];
        if (dates[contactDate] !== undefined) {
            dates[contactDate]++;
        }
    });
    
    // Convert to arrays for Chart.js
    const labels = Object.keys(dates).sort();
    const data = labels.map(date => dates[date]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Contacts Received',
                data: data,
                fill: true,
                backgroundColor: 'rgba(66, 153, 225, 0.2)',
                borderColor: 'rgba(66, 153, 225, 1)',
                tension: 0.3,
                borderWidth: 2,
                pointBackgroundColor: 'rgba(66, 153, 225, 1)',
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 7,
                        color: 'rgba(156, 163, 175, 1)'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(75, 85, 99, 0.2)'
                    },
                    ticks: {
                        stepSize: 1,
                        color: 'rgba(156, 163, 175, 1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    titleColor: 'rgba(255, 255, 255, 1)',
                    bodyColor: 'rgba(255, 255, 255, 1)',
                    borderColor: 'rgba(66, 153, 225, 0.5)',
                    borderWidth: 1,
                    displayColors: false
                }
            }
        }
    });
}

// Delete a contact
async function deleteContact(contactId) {
    try {
        const response = await fetch(`/api/contacts/${contactId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete contact');
        }
        
        // Refresh contacts data after successful deletion
        fetchContacts()
            .then(contacts => {
                renderContactsTable(contacts);
                showSuccessMessage('Contact deleted successfully');
            });
    } catch (error) {
        console.error('Error deleting contact:', error);
        showErrorMessage('Failed to delete contact. Please try again.');
    }
}

// Show success message
function showSuccessMessage(message) {
    // Create a success message element if it doesn't exist
    let successContainer = document.getElementById('success-container');
    if (!successContainer) {
        successContainer = document.createElement('div');
        successContainer.id = 'success-container';
        successContainer.className = 'bg-green-900 bg-opacity-20 text-green-400 p-4 rounded-md mb-4 hidden';
        
        // Insert it before the error container
        const errorContainer = document.getElementById('error-container');
        if (errorContainer && errorContainer.parentNode) {
            errorContainer.parentNode.insertBefore(successContainer, errorContainer);
        }
    }
    
    successContainer.textContent = message;
    successContainer.classList.remove('hidden');
    
    // Hide after 5 seconds
    setTimeout(() => {
        successContainer.classList.add('hidden');
    }, 5000);
}

// Fetch contacts data periodically (every 30 seconds)
function fetchContactsPeriodically() {
    setInterval(() => {
        fetchContacts()
            .then(contacts => {
                renderContactsTable(contacts);
            })
            .catch(error => {
                console.error('Error fetching contacts:', error);
            });
    }, 30000);
}
