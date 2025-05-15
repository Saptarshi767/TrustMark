import os
import logging
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from utils.blockchain import get_user_transactions
from utils.classifier import classify_address
from models import db, FlaggedTransaction

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "trustmark-dev-secret")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)

# Add custom filters
@app.template_filter('datetime')
def format_datetime(value):
    """Format a datetime to a readable string"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    return value.strftime('%b %d, %Y %H:%M') if value else ''

# Create all tables
with app.app_context():
    db.create_all()

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
    
    # Get flagged transactions from the database
    flagged_txs = FlaggedTransaction.query.filter_by(wallet_address=wallet_address).all()
    flagged_tx_dict = {tx.tx_hash: tx.reason for tx in flagged_txs}
    
    # Check which transactions are flagged and add reason
    for tx in transactions:
        if tx['tx_hash'] in flagged_tx_dict:
            tx['flagged'] = True
            tx['flag_reason'] = flagged_tx_dict[tx['tx_hash']]
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


@app.route('/api/flagged_transactions')
def get_flagged_transactions():
    """API endpoint to get all flagged transactions for the current wallet"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Get all flagged transactions for this wallet
    flagged_txs = FlaggedTransaction.query.filter_by(wallet_address=wallet_address).all()
    
    # Convert to dictionary format
    flagged_list = [tx.to_dict() for tx in flagged_txs]
    
    return jsonify({
        'wallet_address': wallet_address,
        'flagged_transactions': flagged_list
    })


@app.route('/flagged_stats')
def flagged_stats():
    """Page showing statistics for flagged transactions"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    # Get all flagged transactions for this wallet
    flagged_txs = FlaggedTransaction.query.filter_by(wallet_address=wallet_address).all()
    
    # Calculate statistics for the charts
    
    # Flag reasons distribution
    reasons = [tx.reason for tx in flagged_txs]
    reason_counter = Counter(reasons)
    flag_reasons = list(reason_counter.keys())
    flag_counts = list(reason_counter.values())
    
    # Set default values if no flagged transactions exist
    if not flag_reasons:
        flag_reasons = ['No Data']
        flag_counts = [0]
    
    # Timeline of flagging activity
    # Group by date
    timeline = defaultdict(int)
    
    # Add today as default if no data
    today = datetime.now().strftime('%Y-%m-%d')
    
    for tx in flagged_txs:
        if tx.created_at:
            date_str = tx.created_at.strftime('%Y-%m-%d')
            timeline[date_str] += 1
    
    # Ensure at least the current date exists
    if not timeline:
        timeline[today] = 0
    
    # Sort by date
    timeline_dates = sorted(timeline.keys())
    timeline_counts = [timeline[date] for date in timeline_dates]
    
    # Format dates for display
    timeline_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%b %d') for date in timeline_dates]
    
    return render_template('flagged_stats.html',
                          wallet_address=wallet_address,
                          flagged_transactions=flagged_txs,
                          flag_reasons=flag_reasons,
                          flag_counts=flag_counts,
                          timeline_dates=timeline_dates,
                          timeline_counts=timeline_counts)

@app.route('/flag_tx', methods=['POST'])
def flag_transaction():
    """API endpoint to flag a transaction"""
    tx_hash = request.form.get('tx_hash')
    flag_reason = request.form.get('flag_reason', 'suspicious')
    wallet_address = session.get('wallet_address')
    
    if not tx_hash:
        return jsonify({'success': False, 'message': 'No transaction hash provided'}), 400
    
    if not wallet_address:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    # Check if already flagged
    existing_flag = FlaggedTransaction.query.filter_by(tx_hash=tx_hash, wallet_address=wallet_address).first()
    
    if existing_flag:
        # Remove flag from database
        db.session.delete(existing_flag)
        db.session.commit()
        flagged = False
        reason = None
    else:
        # Get transaction details for additional context
        transactions = get_user_transactions(wallet_address)
        tx_details = next((tx for tx in transactions if tx['tx_hash'] == tx_hash), None)
        
        # Create new flag
        new_flag = FlaggedTransaction()
        new_flag.tx_hash = tx_hash
        new_flag.wallet_address = wallet_address
        new_flag.reason = flag_reason
        
        if tx_details:
            new_flag.amount = tx_details.get('amount')
            new_flag.direction = tx_details.get('direction')
            new_flag.note = tx_details.get('note')
        
        db.session.add(new_flag)
        db.session.commit()
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
