import os
import logging
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from utils.blockchain import get_user_transactions
from utils.classifier import classify_address

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "trustmark-dev-secret")

# Store flagged transactions in memory with reasons
flagged_transactions = {}

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - simulates wallet connection"""
    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')
        
        # Validate Ethereum address (basic check)
        if wallet_address and wallet_address.startswith('0x') and len(wallet_address) == 42:
            session['wallet_address'] = wallet_address
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter a valid Ethereum address', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard showing transactions"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    # Get transactions for this address
    transactions = get_user_transactions(wallet_address)
    
    # Classify the address based on transactions
    category = classify_address(transactions)
    
    # Check which transactions are flagged and add reason if flagged
    for tx in transactions:
        if tx['tx_hash'] in flagged_transactions:
            tx['flagged'] = True
            tx['flag_reason'] = flagged_transactions[tx['tx_hash']]
        else:
            tx['flagged'] = False
            tx['flag_reason'] = None
    
    return render_template('dashboard.html', 
                          wallet_address=wallet_address, 
                          transactions=transactions,
                          category=category)

@app.route('/classify', methods=['POST'])
def classify():
    """API endpoint to classify an address"""
    data = request.json
    if not data or 'transactions' not in data:
        return jsonify({'error': 'No transaction data provided'}), 400
    
    category = classify_address(data['transactions'])
    return jsonify({'category': category})

@app.route('/flag_tx', methods=['POST'])
def flag_transaction():
    """API endpoint to flag a transaction"""
    tx_hash = request.form.get('tx_hash')
    flag_reason = request.form.get('flag_reason', 'suspicious')
    
    if not tx_hash:
        return jsonify({'success': False, 'message': 'No transaction hash provided'}), 400
    
    # Store or remove flag with reason
    # We're using a dictionary of tx_hash -> reason instead of a simple set
    if tx_hash in flagged_transactions:
        del flagged_transactions[tx_hash]
        flagged = False
        reason = None
    else:
        flagged_transactions[tx_hash] = flag_reason
        flagged = True
        reason = flag_reason
    
    return jsonify({
        'success': True, 
        'flagged': flagged, 
        'tx_hash': tx_hash,
        'reason': reason
    })

@app.route('/logout')
def logout():
    """Log out by removing wallet from session"""
    session.pop('wallet_address', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
