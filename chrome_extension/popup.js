/**
 * TrustMark Chrome Extension Popup Script
 */

// Demo categories to simulate address classification
const demoCategories = [
  'Rookie', 
  'Whale Trader', 
  'Bot', 
  'Hacker', 
  'Whitehat', 
  'Airdrop Hunter', 
  'Liquidity Provider'
];

// Category badge classes
const categoryClasses = {
  'Rookie': 'bg-secondary',
  'Whale Trader': 'bg-primary',
  'Bot': 'bg-info',
  'Hacker': 'bg-danger',
  'Whitehat': 'bg-success',
  'Airdrop Hunter': 'bg-warning',
  'Liquidity Provider': 'bg-info'
};

// Function to scan the current page for Ethereum addresses
function scanPageForAddresses() {
  // Get the current active tab
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    // Send a message to the content script to scan the page
    chrome.tabs.sendMessage(tabs[0].id, {action: "scanPage"}, function(response) {
      if (chrome.runtime.lastError) {
        // Handle error - content script might not be injected yet
        displayError("Could not scan page. Please refresh and try again.");
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

// Function to display found Ethereum addresses
function displayAddresses(addresses) {
  const resultsContainer = document.getElementById('scanResults');
  
  if (addresses.length === 0) {
    displayNoAddresses();
    return;
  }
  
  let html = '';
  addresses.forEach(address => {
    // Assign a random category for demo purposes
    const randomCategory = demoCategories[Math.floor(Math.random() * demoCategories.length)];
    const badgeClass = categoryClasses[randomCategory] || 'bg-secondary';
    
    html += `
      <div class="address-item">
        <div class="d-flex justify-content-between align-items-start">
          <div class="text-truncate me-2">${address}</div>
          <span class="badge ${badgeClass}">${randomCategory}</span>
        </div>
        <div class="mt-2 d-flex gap-1">
          <button class="btn btn-sm btn-outline-warning btn-flag" data-address="${address}">
            <i class="fa fa-flag-o"></i> Flag
          </button>
          <a href="https://trustmark-replit.com/dashboard?address=${address}" target="_blank" class="btn btn-sm btn-outline-primary">
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
  resultsContainer.innerHTML = `
    <div class="text-center text-muted py-3">
      <i class="fa fa-search mb-2 d-block" style="font-size: 2rem;"></i>
      No Ethereum addresses found on this page
    </div>
  `;
}

// Function to display error message
function displayError(message) {
  const resultsContainer = document.getElementById('scanResults');
  resultsContainer.innerHTML = `
    <div class="alert alert-danger">
      <i class="fa fa-exclamation-triangle me-2"></i>
      ${message}
    </div>
  `;
}

// Set up event listeners when the popup loads
document.addEventListener('DOMContentLoaded', function() {
  // Scan button click handler
  document.getElementById('scanPageBtn').addEventListener('click', scanPageForAddresses);
  
  // Simulate scanning the page automatically when popup opens
  // For demo, we'll just show a loading indicator
  const resultsContainer = document.getElementById('scanResults');
  resultsContainer.innerHTML = `
    <div class="text-center py-3">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Ready to scan...</p>
    </div>
  `;
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
