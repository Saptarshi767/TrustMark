/**
 * TrustMark Chrome Extension Popup Script
 */
const BACKEND_URL = 'https://trust-mark.vercel.app';

// DOM Elements
const scanBtn = document.getElementById('scanPageBtn');
const resultsContainer = document.getElementById('scanResults');
const dashboardLink = document.getElementById('dashboardLink');

// --- Functions ---

/**
 * Sends a message to the content script to scan the page for addresses.
 */
function scanPage() {
    resultsContainer.innerHTML = '<div class="text-center text-muted py-3">Scanning...</div>';
    scanBtn.disabled = true;

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length === 0) {
            displayError("Cannot access the current tab.");
            scanBtn.disabled = false;
            return;
        }

        chrome.tabs.sendMessage(tabs[0].id, { action: "scanPage" }, (response) => {
            if (chrome.runtime.lastError) {
                displayError("Could not scan page. Please refresh and try again.");
                scanBtn.disabled = false;
                return;
            }

            if (response && response.addresses && response.addresses.length > 0) {
                displayAddresses(response.addresses);
            } else {
                displayNoAddresses();
            }
            scanBtn.disabled = false;
        });
    });
}

/**
 * Displays the list of found Ethereum addresses in the popup.
 * @param {string[]} addresses - An array of Ethereum addresses.
 */
function displayAddresses(addresses) {
    let html = addresses.map(address => `
        <div class="address-item">
            <div class="d-flex justify-content-between align-items-start">
                <div class="text-truncate me-2">${address}</div>
            </div>
            <div class="mt-2 d-flex gap-1">
                <a href="${BACKEND_URL}/search_results?query=${address}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fa fa-external-link"></i> View on TrustMark
                </a>
            </div>
        </div>
    `).join('');

    resultsContainer.innerHTML = html;
}

/**
 * Displays a message when no addresses are found.
 */
function displayNoAddresses() {
    resultsContainer.innerHTML = `
        <div class="text-center text-muted py-3">
            <i class="fa fa-search mb-2 d-block" style="font-size: 2rem;"></i>
            No Ethereum addresses found on this page.
        </div>`;
}

/**
 * Displays an error message in the results container.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    resultsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fa fa-exclamation-triangle me-2"></i>
            ${message}
        </div>`;
}

/**
 * Sets the initial state of the popup.
 */
function setInitialState() {
    if (dashboardLink) {
        dashboardLink.href = `${BACKEND_URL}/dashboard`;
    }
    
    resultsContainer.innerHTML = `
        <div class="text-center text-muted py-3">
            <i class="fa fa-info-circle mb-2 d-block" style="font-size: 2rem;"></i>
            Click "Scan Current Page" to detect Ethereum addresses.
        </div>`;
}

// --- Event Listeners ---

document.addEventListener('DOMContentLoaded', () => {
    setInitialState();
    scanBtn.addEventListener('click', scanPage);
});
