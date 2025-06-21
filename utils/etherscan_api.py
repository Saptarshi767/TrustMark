"""
Etherscan API integration for TrustMark
Fetches real transaction data from Ethereum blockchain
"""
import os
import logging
import json
import requests
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Constants
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
API_KEY = os.environ.get("ETHERSCAN_API_KEY", "IRI57XAY533YXUSDTU9J9TU6ZY9B4IWSRS")

def convert_timestamp(timestamp):
    """Convert Unix timestamp to datetime object"""
    return datetime.fromtimestamp(int(timestamp))

def format_amount(amount_wei):
    """Convert Wei amount to Ether"""
    try:
        amount_ether = float(amount_wei) / 10**18
        return round(amount_ether, 6)
    except (ValueError, TypeError):
        return 0

def get_transaction_history(address, limit=100):
    """
    Fetch transaction history for an Ethereum address using Etherscan API
    
    Parameters:
    - address (str): Ethereum wallet address
    - limit (int): Maximum number of transactions to return
    
    Returns:
    - list: Transactions in standardized format
    """
    if not API_KEY:
        logger.error("Etherscan API key not found in environment variables")
        return []
    
    if not address or not address.startswith('0x'):
        logger.error(f"Invalid Ethereum address: {address}")
        return []
    
    # Make API calls to get normal and internal transactions
    transactions = []
    
    # Get normal transactions
    try:
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': limit,
            'sort': 'desc',
            'apikey': API_KEY
        }
        
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == '1':
            txs = data['result']
            for tx in txs:
                # Determine if this is incoming or outgoing
                direction = 'in' if tx['to'].lower() == address.lower() else 'out'
                
                # Check if this is a contract call
                is_contract_call = tx['input'] != '0x'
                
                # Get transaction note/type
                note = ''
                if is_contract_call:
                    note = 'contract call'
                elif tx.get('functionName'):
                    note = tx['functionName'].split('(')[0][:20]  # Truncate function name
                
                # Format transaction
                formatted_tx = {
                    'tx_hash': tx['hash'],
                    'amount': format_amount(tx['value']),
                    'direction': direction,
                    'note': note,
                    'timestamp': convert_timestamp(tx['timeStamp']),
                    'contract_call': is_contract_call,
                    'from': tx['from'],
                    'to': tx['to'],
                    'gas': int(tx['gas']),
                    'gas_price': int(tx['gasPrice']),
                    'block_number': int(tx['blockNumber'])
                }
                
                transactions.append(formatted_tx)
        else:
            logger.error(f"Etherscan API error: {data.get('message', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Error fetching transactions from Etherscan: {str(e)}")
    
    # Sort transactions by timestamp
    transactions.sort(key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
    
    return transactions[:limit]

def get_transaction_details(tx_hash):
    """
    Get detailed information about a specific transaction
    
    Parameters:
    - tx_hash (str): Transaction hash
    
    Returns:
    - dict: Transaction details or None if not found
    """
    if not API_KEY:
        logger.error("Etherscan API key not found in environment variables")
        return None
    
    try:
        params = {
            'module': 'proxy',
            'action': 'eth_getTransactionByHash',
            'txhash': tx_hash,
            'apikey': API_KEY
        }
        
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get('result'):
            tx = data['result']
            
            # Format transaction
            formatted_tx = {
                'tx_hash': tx['hash'],
                'amount': format_amount(int(tx['value'], 16) if tx['value'].startswith('0x') else tx['value']),
                'from': tx['from'],
                'to': tx['to'],
                'gas': int(tx['gas'], 16) if tx['gas'].startswith('0x') else int(tx['gas']),
                'gas_price': int(tx['gasPrice'], 16) if tx['gasPrice'].startswith('0x') else int(tx['gasPrice']),
                'data': tx['input'],
                'block_number': int(tx['blockNumber'], 16) if tx['blockNumber'] and tx['blockNumber'].startswith('0x') else tx['blockNumber'],
                'is_contract_call': tx['input'] != '0x'
            }
            
            return formatted_tx
        else:
            logger.error(f"Etherscan API error: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
    
    except Exception as e:
        logger.error(f"Error fetching transaction details from Etherscan: {str(e)}")
        return None

def get_ether_balance(address):
    """
    Get the current ETH balance of an address
    
    Parameters:
    - address (str): Ethereum wallet address
    
    Returns:
    - float: Balance in Ether
    """
    if not API_KEY:
        logger.error("Etherscan API key not found in environment variables")
        return 0
    
    try:
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': API_KEY
        }
        
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == '1':
            return format_amount(data['result'])
        else:
            logger.error(f"Etherscan API error: {data.get('message', 'Unknown error')}")
            return 0
    
    except Exception as e:
        logger.error(f"Error fetching balance from Etherscan: {str(e)}")
        return 0