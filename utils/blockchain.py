"""
Mock Ethereum blockchain data retrieval utility
"""

def get_user_transactions(address):
    """
    Returns a mock transaction history for a wallet address
    
    Parameters:
    - address (str): Ethereum wallet address
    
    Returns:
    - list: A list of transaction dictionaries
    """
    # Generate different transactions based on address hash
    # This gives different users different transaction patterns
    transactions = []
    
    # Generate mock transaction count based on address last char
    tx_count = int(address[-1], 16) + 1  # 1-16 transactions
    
    # For each transaction, create a mock record
    for i in range(tx_count):
        tx_hash = f"0x{i}{'0'*60}{i}"
        
        # Alternate between incoming and outgoing
        direction = "in" if i % 2 == 0 else "out"
        
        # Use some characteristics based on address to make transactions look different
        amount = (int(address[-2:], 16) * 1000) / (i + 1)
        
        # Determine transaction type/note
        note = ""
        if i % 7 == 0:
            note = "airdrop"
        elif i % 11 == 0:
            note = "exploit"
        elif i % 13 == 0:
            note = "audit"
        elif i % 5 == 0:
            note = "contract call"
        
        transactions.append({
            "tx_hash": tx_hash,
            "amount": round(amount, 4),
            "direction": direction,
            "note": note,
            "contract_call": i % 3 == 0,  # Every third transaction is a contract call
        })
    
    return transactions
