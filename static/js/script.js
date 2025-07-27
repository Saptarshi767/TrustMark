/**
 * TrustMark - Main JavaScript
 */

// Detect MetaMask
function detectMetaMask() {
    return window.ethereum && window.ethereum.isMetaMask;
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // MetaMask integration is handled in login.html template directly
    // No need to create duplicate buttons here
    
    // Handle transaction hovering
    const txRows = document.querySelectorAll('tr[id^="tx-"]');
    txRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('bg-dark-subtle');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('bg-dark-subtle');
        });
    });
});

// Helper function to truncate Ethereum addresses
function truncateAddress(address, prefixLength = 6, suffixLength = 4) {
    if (!address) return '';
    if (address.length <= prefixLength + suffixLength) return address;
    
    return `${address.slice(0, prefixLength)}...${address.slice(-suffixLength)}`;
}

// For copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        function() {
            // Success
            const tooltip = document.createElement('div');
            tooltip.className = 'position-fixed top-0 end-0 p-3';
            tooltip.style.zIndex = '1070';
            
            tooltip.innerHTML = `
                <div class="toast show" role="alert">
                    <div class="toast-header">
                        <strong class="me-auto">TrustMark</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        Copied to clipboard!
                    </div>
                </div>
            `;
            
            document.body.appendChild(tooltip);
            
            setTimeout(() => {
                tooltip.remove();
            }, 2000);
        },
        function() {
            // Error
            console.error('Failed to copy text');
        }
    );
}
