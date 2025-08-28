import os
import logging
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from utils.etherscan_api import get_transaction_history, get_ether_balance, get_transaction_details
from utils.classifier import classify_address
from models import db, FlaggedTransaction
from web3 import Web3
import secrets
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "trustmark-dev-secret")

# Add CORS support for Chrome extension
@app.after_request
def after_request(response):
    # Only allow requests from the extension and the app itself
    origin = request.headers.get('Origin')
    allowed_origins = [
        'https://trust-mark.vercel.app',
        'chrome-extension://*'  # Allow Chrome extension
    ]
    
    # Check if origin matches allowed patterns
    if origin and any(origin.startswith(allowed.replace('*', '')) for allowed in allowed_origins):
        response.headers.add('Access-Control-Allow-Origin', origin)
    elif not origin:  # Same-origin requests
        response.headers.add('Access-Control-Allow-Origin', 'https://trust-mark.vercel.app')
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # Add CSP header (security headers are handled by vercel.json)
    response.headers.add('Content-Security-Policy', 
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.etherscan.io; "
        "font-src 'self' https://cdn.jsdelivr.net;"
    )
    
    return response

# --- Database Configuration ---
def configure_database():
    """Configure database with fallback options"""
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        try:
            # Use Neon PostgreSQL database
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
            }
            print("Configured Neon PostgreSQL database.")
            return True
        except Exception as e:
            print(f"PostgreSQL configuration failed: {e}")
    
    # Fallback to SQLite
    try:
        # Use in-memory SQLite for Vercel (since file system is read-only)
        if os.environ.get('VERCEL'):
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
            print("Using in-memory SQLite database for Vercel.")
        else:
            # Local file-based SQLite for development
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'trustmark.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
            print(f"Using local SQLite DB at {db_path}")
        return True
    except Exception as e:
        print(f"SQLite configuration failed: {e}")
        return False

# Configure database
configure_database()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

# Create all tables (only in development or when explicitly needed)
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Lazy database initialization
def ensure_db():
    """Ensure database is initialized, but don't fail if it's not"""
    try:
        # Try to query the database to see if it's working
        with app.app_context():
            from models import FlaggedTransaction
            FlaggedTransaction.query.first()
        return True
    except Exception:
        # If query fails, try to initialize
        return init_db()

# Only create tables if running directly (not in production)
if __name__ == '__main__':
    init_db()

@app.route('/')
def index():
    """Landing page"""
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback if template loading fails
        return jsonify({
            'message': 'TrustMark API is running',
            'error': f'Template loading failed: {str(e)}',
            'endpoints': ['/health', '/login', '/dashboard', '/api/flagged_addresses']
        })

@app.route('/health')
def health_check():
    """Health check endpoint for deployment verification"""
    db_status = 'unknown'
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute(db.text('SELECT 1'))
            result.fetchone()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)[:50]}'
    
    return jsonify({
        'status': 'healthy',
        'message': 'TrustMark API is running',
        'database': db_status,
        'environment': {
            'DATABASE_URL': 'set' if os.environ.get('DATABASE_URL') else 'missing',
            'ETHERSCAN_API_KEY': 'set' if os.environ.get('ETHERSCAN_API_KEY') else 'missing',
            'SESSION_SECRET': 'set' if os.environ.get('SESSION_SECRET') else 'missing'
        }
    })

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
    
    # Get real transactions from Etherscan API
    try:
        transactions = get_transaction_history(wallet_address)
        if not transactions:
            flash('No transactions found for this address.', 'info')
            transactions = []
    except Exception as e:
        logging.error(f"Error fetching transactions from Etherscan: {str(e)}")
        flash('Error fetching transactions from Etherscan.', 'danger')
        transactions = []
    
    # Get current balance
    try:
        balance = get_ether_balance(wallet_address)
    except Exception:
        balance = 0
    
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
                          category=category,
                          balance=balance)

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


@app.route('/api/flagged_addresses')
def get_flagged_addresses():
    """API endpoint for Chrome extension to get all flagged addresses"""
    # Get all unique flagged addresses from the database
    flagged_addresses = db.session.query(FlaggedTransaction.wallet_address).distinct().all()
    
    # Convert to list of addresses
    addresses = [addr[0] for addr in flagged_addresses]
    
    # Also get addresses that appear in flagged transactions (as they might be suspicious)
    flagged_tx_addresses = db.session.query(FlaggedTransaction.wallet_address).all()
    tx_addresses = [addr[0] for addr in flagged_tx_addresses]
    
    return jsonify({
        'flagged_addresses': addresses,
        'suspicious_addresses': tx_addresses,
        'total_flagged': len(addresses),
        'total_suspicious': len(tx_addresses)
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
        # Try to get transaction details from Etherscan first
        try:
            tx_details = get_transaction_details(tx_hash)
        except Exception as e:
            logging.error(f"Error fetching transaction details from Etherscan: {str(e)}")
            tx_details = None
            
        # If not found, try to find in recent transactions
        if not tx_details:
            try:
                transactions = get_transaction_history(wallet_address)
                tx_details = next((tx for tx in transactions if tx['tx_hash'] == tx_hash), None)
            except Exception:
                tx_details = None
        
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

@app.route('/transaction/<tx_hash>')
def transaction_details(tx_hash):
    """Show details for a specific transaction"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    # Try to get transaction details from Etherscan
    try:
        tx = get_transaction_details(tx_hash)
    except Exception as e:
        logging.error(f"Error fetching transaction details from Etherscan: {str(e)}")
        tx = None
    
    # If not found, try to find in recent transactions
    if not tx:
        try:
            transactions = get_transaction_history(wallet_address)
            tx = next((t for t in transactions if t['tx_hash'] == tx_hash), None)
        except Exception:
            tx = None
    
    if not tx:
        flash('Transaction not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if the transaction is flagged
    flag = FlaggedTransaction.query.filter_by(tx_hash=tx_hash, wallet_address=wallet_address).first()
    tx_is_flagged = flag is not None
    flag_reason = flag.reason if flag else None
    
    return render_template(
        'transaction_details.html',
        wallet_address=wallet_address,
        tx=tx,
        tx_is_flagged=tx_is_flagged,
        flag_reason=flag_reason
    )


@app.route('/search')
def search():
    """Search form for Ethereum addresses"""
    wallet_address = session.get('wallet_address')
    logged_in = wallet_address is not None
    
    return render_template('search.html', logged_in=logged_in)


@app.route('/search/results')
def search_results():
    """Show analysis results for an Ethereum address"""
    address = request.args.get('address')
    
    if not address:
        flash('Please enter an Ethereum address', 'warning')
        return redirect(url_for('search'))
    
    # Basic validation
    if not address.startswith('0x') or len(address) != 42:
        flash('Invalid Ethereum address format', 'danger')
        return redirect(url_for('search'))
    
    # Get current user's wallet address from session
    wallet_address = session.get('wallet_address')
    logged_in = wallet_address is not None
    is_my_address = logged_in and wallet_address.lower() == address.lower()
    
    # Get transactions and balance from Etherscan
    try:
        transactions = get_transaction_history(address)
        balance = get_ether_balance(address)
        
        # Use classifier to determine category
        category = classify_address(transactions)
        
    except Exception as e:
        logging.error(f"Error fetching Etherscan data: {str(e)}")
        flash('Error fetching blockchain data. Please try again later.', 'danger')
        return redirect(url_for('search'))
    
    return render_template(
        'search_results.html',
        address=address,
        transactions=transactions,
        category=category,
        balance=balance,
        logged_in=logged_in,
        is_my_address=is_my_address
    )


@app.route('/logout')
def logout():
    """Log out by removing wallet from session"""
    session.pop('wallet_address', None)
    return redirect(url_for('index'))

@app.route('/extension-guide')
def extension_guide():
    """Chrome extension installation guide"""
    return render_template('extension_guide.html')

@app.route('/api/nonce')
def get_nonce():
    address = request.args.get('address')
    if not address or not address.startswith('0x'):
        return jsonify({'error': 'Invalid address'}), 400
    nonce = secrets.token_hex(16)
    session['siwe_nonce'] = nonce
    session['siwe_address'] = address.lower()
    return jsonify({'nonce': nonce})

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    address = data.get('address', '').lower()
    signature = data.get('signature')
    nonce = data.get('nonce')
    expected_nonce = session.get('siwe_nonce')
    expected_address = session.get('siwe_address')
    if not (address and signature and nonce and expected_nonce and expected_address):
        return jsonify({'success': False, 'message': 'Missing data'}), 400
    if nonce != expected_nonce or address != expected_address:
        return jsonify({'success': False, 'message': 'Invalid nonce or address'}), 400
    # Verify signature
    w3 = Web3()
    message = f'Sign this message to login: {nonce}'
    try:
        recovered = w3.eth.account.recover_message(text=message, signature=signature)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Signature verification failed: {str(e)}'}), 400
    if recovered.lower() != address:
        return jsonify({'success': False, 'message': 'Signature does not match address'}), 400
    # Success: log in user
    session['wallet_address'] = address
    session.pop('siwe_nonce', None)
    session.pop('siwe_address', None)
    return jsonify({'success': True})

# For Vercel deployment
def create_app():
    """Application factory for production deployment"""
    try:
        load_dotenv()
        
        # Initialize database tables if needed
        with app.app_context():
            try:
                db.create_all()
                print("Database tables initialized successfully")
            except Exception as db_error:
                print(f"Database initialization warning: {db_error}")
                # Continue without database if it fails
        
        return app
    except Exception as e:
        print(f"Error in create_app: {e}")
        raise

# Vercel entry point
application = create_app()

if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', port=5000, debug=True)
