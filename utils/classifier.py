"""
Classifier utility for categorizing Ethereum addresses
"""

def classify_address(tx_list):
    """
    Classifies an address based on its transaction history
    
    Parameters:
    - tx_list (list): List of transactions for an address
    
    Returns:
    - str: Classification category
    """
    # If no transactions, default to Rookie
    if not tx_list:
        return "Rookie"
    
    # Get transaction count
    tx_count = len(tx_list)
    
    # Count contract calls
    contract_calls = sum(1 for tx in tx_list if tx.get('contract_call', False))
    
    # Calculate total volume
    total_volume = sum(tx.get('amount', 0) for tx in tx_list)
    
    # Check for specific transaction notes
    airdrop_notes = sum(1 for tx in tx_list if tx.get('note') == "airdrop")
    exploit_notes = sum(1 for tx in tx_list if tx.get('note') == "exploit")
    audit_notes = sum(1 for tx in tx_list if tx.get('note') == "audit")
    
    # Classification Logic per requirements:
    
    # Whitehat has highest priority
    if audit_notes > 0:
        return "Whitehat"
    
    # Hacker has second priority
    if exploit_notes > 0:
        return "Hacker"
    
    # Airdrop Hunter priority
    if airdrop_notes > 0:
        return "Airdrop Hunter"
    
    # Bot has next priority
    if contract_calls > 10:
        return "Bot"
    
    # Whale Trader has next priority
    if total_volume > 100000:
        return "Whale Trader"
    
    # Liquidity Provider check (high volume transactions)
    high_volume_txs = sum(1 for tx in tx_list if tx.get('amount', 0) > 10000)
    if high_volume_txs >= 2:
        return "Liquidity Provider"
        
    # Rookie gets lowest priority
    if tx_count < 5:
        return "Rookie"
    
    # Default fallback
    return "Standard User"
