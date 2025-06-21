// content.js
// TrustMark Chrome Extension - Modern Themed Content Script
// Highlights Ethereum addresses on the page with a modern glassmorphism badge
// Fetches flagged addresses from local TrustMark backend

(function() {
    // Regex for Ethereum addresses (ensures it's not part of a longer hex string)
    const ethAddressRegex = /b(0x[a-fA-F0-9]{40})b/g;
    
    // TrustMark Backend URL - Deployed on Vercel
    const BACKEND_URL = 'https://trust-mark.vercel.app';
    
    // Store flagged addresses
    let flaggedAddresses = [];
    let suspiciousAddresses = [];
    
    // Modern badge styles
    const normalBadgeStyle = `
        display: inline-block;
        background: linear-gradient(90deg, #5f72ff 0%, #9a5cff 100%);
        color: #fff;
        font-size: 0.85em;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        border-radius: 12px;
        box-shadow: 0 2px 8px 0 rgba(90, 60, 255, 0.18);
        padding: 2px 10px;
        margin-left: 6px;
        vertical-align: middle;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: 1.5px solid rgba(255,255,255,0.12);
        backdrop-filter: blur(4px);
        transition: background 0.3s;
    `;
    
    const flaggedBadgeStyle = `
        display: inline-block;
        background: linear-gradient(90deg, #ff4757 0%, #ff3742 100%);
        color: #fff;
        font-size: 0.85em;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        border-radius: 12px;
        box-shadow: 0 2px 8px 0 rgba(255, 71, 87, 0.3);
        padding: 2px 10px;
        margin-left: 6px;
        vertical-align: middle;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: 1.5px solid rgba(255,255,255,0.12);
        backdrop-filter: blur(4px);
        transition: background 0.3s;
        position: relative;
    `;
    
    const suspiciousBadgeStyle = `
        display: inline-block;
        background: linear-gradient(90deg, #ffa502 0%, #ff9500 100%);
        color: #fff;
        font-size: 0.85em;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        border-radius: 12px;
        box-shadow: 0 2px 8px 0 rgba(255, 165, 2, 0.3);
        padding: 2px 10px;
        margin-left: 6px;
        vertical-align: middle;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: 1.5px solid rgba(255,255,255,0.12);
        backdrop-filter: blur(4px);
        transition: background 0.3s;
    `;
    
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
            } else {
                console.warn('TrustMark: Failed to fetch flagged addresses:', response.status);
            }
        } catch (error) {
            console.warn('TrustMark: Error fetching flagged addresses:', error);
        }
    }
    
    // Check if an address is flagged or suspicious
    function getAddressStatus(address) {
        const lowerAddress = address.toLowerCase();
        if (flaggedAddresses.some(addr => addr.toLowerCase() === lowerAddress)) {
            return 'flagged';
        } else if (suspiciousAddresses.some(addr => addr.toLowerCase() === lowerAddress)) {
            return 'suspicious';
        }
        return 'normal';
    }
    
    // Get appropriate badge style based on address status
    function getBadgeStyle(status) {
        switch (status) {
            case 'flagged':
                return flaggedBadgeStyle;
            case 'suspicious':
                return suspiciousBadgeStyle;
            default:
                return normalBadgeStyle;
        }
    }
    
    // Get badge text based on status
    function getBadgeText(address, status) {
        switch (status) {
            case 'flagged':
                return `${address} ⚠️ FLAGGED`;
            case 'suspicious':
                return `${address} ⚡ SUSPICIOUS`;
            default:
                return address;
        }
    }
    
    // Scan all text nodes and highlight ETH addresses
    function highlightAddresses(node) {
        if (node.nodeType === 3 && node.textContent.match(ethAddressRegex)) {
            const span = document.createElement('span');
            span.innerHTML = node.textContent.replace(ethAddressRegex, function(addr) {
                const status = getAddressStatus(addr);
                const style = getBadgeStyle(status);
                const text = getBadgeText(addr, status);
                return `<span class='trustmark-badge trustmark-${status}' style="${style}" title="TrustMark: ${status.toUpperCase()}">${text}</span>`;
            });
            node.parentNode.replaceChild(span, node);
        } else if (node.nodeType === 1 && node.childNodes && !['SCRIPT','STYLE','TEXTAREA','INPUT'].includes(node.tagName)) {
            for (let i = 0; i < node.childNodes.length; i++) {
                highlightAddresses(node.childNodes[i]);
            }
        }
    }
    
    // Initialize extension
    async function initialize() {
        // Fetch flagged addresses first
        await fetchFlaggedAddresses();
        
        // Then highlight addresses on the page
        highlightAddresses(document.body);
        
        // Set up observer for dynamic content
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) {
                            highlightAddresses(node);
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Refresh flagged addresses every 5 minutes
    setInterval(fetchFlaggedAddresses, 5 * 60 * 1000);

    /**
     * Finds all unique Ethereum addresses on the page.
     * This function is designed to be efficient by using TreeWalker.
     */
    function findAddresses() {
        const addresses = new Set();
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while (node = walker.nextNode()) {
            // Skip script and style content
            const parentTag = node.parentElement.tagName;
            if (parentTag === 'SCRIPT' || parentTag === 'STYLE') {
                continue;
            }
            
            const matches = node.nodeValue.match(ethAddressRegex);
            if (matches) {
                matches.forEach(addr => addresses.add(addr));
            }
        }
        return Array.from(addresses);
    }

    // Listen for a message from the popup script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === "scanPage") {
            try {
                const uniqueAddresses = findAddresses();
                sendResponse({ addresses: uniqueAddresses });
            } catch (error) {
                console.error("TrustMark: Error scanning page:", error);
                sendResponse({ addresses: [], error: "Failed to scan the page." });
            }
        }
        // Return true to indicate you wish to send a response asynchronously
        return true;
    });
})(); 