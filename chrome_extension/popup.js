/**
 * TrustMark Chrome Extension Popup Script
 */

// TrustMark Backend URL - Use localhost for testing, Vercel for production
const BACKEND_URL = 'http://localhost:5000'; // Change to 'https://trust-mark.vercel.app' for production

// Store flagged addresses
let flaggedAddresses = [];
let suspiciousAddresses = [];

// Category badge classes with purple theme
const categoryClasses = {
  'Rookie': 'bg-secondary',
  'Whale Trader': 'bg-primary', 
  'Bot': 'bg-info',
  'Hacker': 'bg-danger',
  'Whitehat': 'bg-success',
  'Airdrop Hunter': 'bg-warning',
  'Liquidity Provider': 'bg-info',
  'Flagged': 'bg-danger',
  'Suspicious': 'bg-warning',
  'Normal': 'bg-secondary'
};

// Fetch flagged addresses from backend
async function fetchFlaggedAddresses() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/flagged_addresses`);
    if (response.ok) {
      const data = await response.json();
      flaggedAddresses = data.flagged_addresses || [];
      suspiciousAddresses = data.suspicious_addresses || [];
      console.log('TrustMark: Loaded flagged addresses:', flaggedAddresses.length);
      console.log('TrustMark: Loaded suspicious addresses:', suspiciousAddresses.length);
      return true;
    } else {
      console.warn('TrustMark: Failed to fetch flagged addresses:', response.status);
      return false;
    }
  } catch (error) {
    console.warn('TrustMark: Error fetching flagged addresses:', error);
    return false;
  }
}

// Function to scan the current page for Ethereum addresses
function scanPageForAddresses() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { action: "scanPage" }, function(response) {
      if (chrome.runtime.lastError) {
        displayError("Could not scan page. Please refresh the page and try again.");
        return;
      }
      if (response && response.addresses) {
        displayAddresses(response.addresses);
      } else {
        displayNoAddresses();
      }
    });
  });
}

// Function to check if an address is flagged or suspicious
function getAddressStatus(address) {
  const lowerAddress = address.toLowerCase();
  if (flaggedAddresses.some(addr => addr.toLowerCase() === lowerAddress)) {
    return 'Flagged';
  } else if (suspiciousAddresses.some(addr => addr.toLowerCase() === lowerAddress)) {
    return 'Suspicious';
  }
  return 'Normal';
}

// Function to display found Ethereum addresses
function displayAddresses(addresses) {
  const resultsContainer = document.getElementById('scanResults');
  
  if (addresses.length === 0) {
    displayNoAddresses();
    return;
  }
  
  let html = '';
  addresses.forEach(address => {
    const status = getAddressStatus(address);
    const badgeClass = categoryClasses[status] || 'bg-secondary';
    
    html += `
      <div class="address-item">
        <div class="d-flex justify-content-between align-items-start">
          <div class="text-truncate me-2">${address}</div>
          <span class="badge ${badgeClass}">${status}</span>
        </div>
        <div class="mt-2 d-flex gap-1">
          <button class="btn btn-sm btn-outline-warning btn-flag" data-address="${address}">
            <i class="fa fa-flag-o"></i> Flag
          </button>
          <a href="${BACKEND_URL}/search?address=${address}" target="_blank" class="btn btn-sm btn-outline-primary">
            <i class="fa fa-external-link"></i> View
          </a>
        </div>
      </div>
    `;
  });
  
  resultsContainer.innerHTML = html;
  
  // Add event listeners to flag buttons
  document.querySelectorAll('.btn-flag').forEach(button => {
    button.addEventListener('click', function() {
      const address = this.getAttribute('data-address');
      this.innerHTML = '<i class="fa fa-flag"></i> Flagged';
      this.classList.remove('btn-outline-warning');
      this.classList.add('btn-warning');
      this.disabled = true;
      
      // In a real extension, this would send the flag to the server
      console.log('Flagged address:', address);
    });
  });
}

// Function to display a "no addresses found" message
function displayNoAddresses() {
  const resultsContainer = document.getElementById('scanResults');
  resultsContainer.innerHTML = `<div class="text-center text-muted py-3"><i class="fa fa-search mb-2 d-block fs-2"></i>No Ethereum addresses found.</div>`;
}

// Function to display error message
function displayError(message) {
  const resultsContainer = document.getElementById('scanResults');
  resultsContainer.innerHTML = `<div class="alert alert-danger"><i class="fa fa-exclamation-triangle me-2"></i>${message}</div>`;
}

// Function to display loading message
function displayLoading(message) {
  const resultsContainer = document.getElementById('scanResults');
  resultsContainer.innerHTML = `
    <div class="text-center py-3">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">${message}</p>
    </div>
  `;
}

// Set up event listeners when the popup loads
document.addEventListener('DOMContentLoaded', async function() {
  // Set the dashboard link href dynamically
  const dashboardLink = document.getElementById('dashboardLink');
  if(dashboardLink) {
    dashboardLink.href = `${BACKEND_URL}/login`;
  }
  
  const scanBtn = document.getElementById('scanPageBtn');
  scanBtn.addEventListener('click', scanPageForAddresses);
  
  displayLoading('Initializing TrustMark...');
  
  // Fetch flagged addresses from backend
  const success = await fetchFlaggedAddresses();
  
  if (success) {
    // Show ready message
    const resultsContainer = document.getElementById('scanResults');
    resultsContainer.innerHTML = `
      <div class="text-center text-muted py-3">
        <i class="fa fa-check-circle text-success mb-2 d-block fs-2"></i>
        TrustMark is ready. Click "Scan" to begin.
      </div>
    `;
  } else {
    displayError(`Failed to connect to TrustMark backend.`);
  }
});

// Function to mock scanning process (for demo purposes)
// In a real extension, this would be handled by a content script
function mockScanDemo() {
  // For demo purposes, sometimes show addresses, sometimes show empty result
  const shouldShowAddresses = Math.random() > 0.3;
  
  if (shouldShowAddresses) {
    // Generate some mock Ethereum addresses
    const mockAddresses = [
      '0x71C7656EC7ab88b098defB751B7401B5f6d8976F',
      '0x2546BcD3c84621e976D8185a91A922aE77ECEc30'
    ];
    
    // Show a random number of addresses (1 or 2)
    const addressesToShow = Math.random() > 0.5 ? mockAddresses : [mockAddresses[0]];
    
    displayAddresses(addressesToShow);
  } else {
    displayNoAddresses();
  }
}
