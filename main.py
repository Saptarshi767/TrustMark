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

# Security middleware
@app.before_request
def security_middleware():
    """Enhanced security checks before processing requests"""
    
    # Block requests with suspicious user agents
    user_agent = request.headers.get('User-Agent', '').lower()
    suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
    
    # Allow legitimate bots but block malicious ones
    if any(agent in user_agent for agent in suspicious_agents):
        if not any(legit in user_agent for legit in ['googlebot', 'bingbot', 'slurp']):
            from flask import abort
            abort(403)
    
    # Rate limiting by IP for sensitive endpoints
    if request.endpoint in ['login', 'get_nonce', 'authenticate']:
        client_ip = request.remote_addr
        rate_key = f"requests_{client_ip}_{request.endpoint}"
        
        # Get current request count
        current_count = session.get(rate_key, 0)
        
        # Different limits for different endpoints
        limits = {
            'login': 20,      # 20 login page requests per session
            'get_nonce': 10,  # 10 nonce requests per session  
            'authenticate': 5  # 5 auth attempts per session
        }
        
        if current_count >= limits.get(request.endpoint, 10):
            from flask import abort
            abort(429)  # Too Many Requests
        
        session[rate_key] = current_count + 1

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
    
    # Add strict security headers with nonce for inline scripts
    nonce = secrets.token_urlsafe(16)
    response.headers.add('Content-Security-Policy', 
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
        f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        f"img-src 'self' data: https://cdn.iconscout.com; "
        f"connect-src 'self' https://api.etherscan.io; "
        f"font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self'; "
        f"upgrade-insecure-requests;"
    )
    
    # Additional security headers
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    response.headers.add('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.add('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    response.headers.add('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
    response.headers.add('Cross-Origin-Embedder-Policy', 'require-corp')
    response.headers.add('Cross-Origin-Opener-Policy', 'same-origin')
    response.headers.add('Cross-Origin-Resource-Policy', 'same-origin')
    
    # Remove server information
    response.headers.pop('Server', None)
    
    # Store nonce in Flask's g object for template access
    from flask import g
    g.csp_nonce = nonce
    
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
        # Fallback HTML page if template loading fails
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TrustMark - Decentralized Reputation Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
            <style>
                body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .hero {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; }}
                .glass-card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 15px; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">
                        <i class="fa fa-shield me-2"></i>TrustMark
                    </a>
                    <div class="navbar-nav ms-auto">
                        <a class="nav-link" href="/login">Login</a>
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                        <a class="nav-link" href="/search">Search</a>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-5">
                <div class="hero p-5 text-white text-center">
                    <h1 class="display-3 fw-bold mb-3">TrustMark</h1>
                    <p class="lead mb-4">A decentralized reputation tagging platform for Ethereum</p>
                    <div class="d-flex justify-content-center gap-3 mb-4 flex-wrap">
                        <a href="/login" class="btn btn-light btn-lg">
                            <i class="fa fa-wallet me-2"></i>Login with Wallet
                        </a>
                        <a href="/dashboard" class="btn btn-outline-light btn-lg">
                            <i class="fa fa-dashboard me-2"></i>View Dashboard
                        </a>
                    </div>
                </div>
                
                <div class="row mt-5">
                    <div class="col-md-4 mb-4">
                        <div class="glass-card p-4 text-white text-center h-100">
                            <i class="fa fa-search fa-3x mb-3"></i>
                            <h3>Transaction Analysis</h3>
                            <p>Advanced analysis of Ethereum wallet transactions to identify patterns and behaviors.</p>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="glass-card p-4 text-white text-center h-100">
                            <i class="fa fa-tags fa-3x mb-3"></i>
                            <h3>Address Classification</h3>
                            <p>Intelligent classification of addresses into categories like Rookie, Whale Trader, Bot, and more.</p>
                        </div>
                    </div>
                    <div class="col-md-4 mb-4">
                        <div class="glass-card p-4 text-white text-center h-100">
                            <i class="fa fa-flag fa-3x mb-3"></i>
                            <h3>Flag Suspicious Activity</h3>
                            <p>Community-driven flagging system to mark suspicious transactions and protect users.</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for search engines"""
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml for search engines"""
    from flask import send_from_directory
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

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
        wallet_address = request.form.get('wallet_address', '').strip()
        
        # Enhanced validation for Ethereum address
        if wallet_address:
            # Remove any whitespace and convert to lowercase for validation
            wallet_address = wallet_address.lower()
            
            # Validate Ethereum address format
            if (wallet_address.startswith('0x') and 
                len(wallet_address) == 42 and 
                all(c in '0123456789abcdef' for c in wallet_address[2:])):
                
                # Additional security: Rate limiting check
                session_key = f"login_attempts_{request.remote_addr}"
                attempts = session.get(session_key, 0)
                
                if attempts >= 5:
                    flash('Too many login attempts. Please try again later.', 'danger')
                    return render_template('login.html')
                
                # Store the validated address
                session['wallet_address'] = wallet_address
                session.pop(session_key, None)  # Clear attempts on success
                
                return redirect(url_for('dashboard'))
            else:
                # Increment failed attempts
                session[session_key] = attempts + 1
                flash('Please enter a valid Ethereum address (42 characters starting with 0x)', 'danger')
        else:
            flash('Wallet address is required', 'danger')
    
    # Generate CSP nonce for inline scripts
    from flask import g
    nonce = getattr(g, 'csp_nonce', secrets.token_urlsafe(16))
    
    return render_template('login.html', csp_nonce=nonce)

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
    # Rate limiting check
    client_ip = request.remote_addr
    rate_limit_key = f"nonce_requests_{client_ip}"
    requests_count = session.get(rate_limit_key, 0)
    
    if requests_count >= 10:  # Max 10 nonce requests per session
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    address = request.args.get('address', '').strip().lower()
    
    # Enhanced validation
    if not address or not address.startswith('0x') or len(address) != 42:
        return jsonify({'error': 'Invalid Ethereum address format'}), 400
    
    # Validate hex characters
    try:
        int(address[2:], 16)
    except ValueError:
        return jsonify({'error': 'Invalid Ethereum address characters'}), 400
    
    # Generate secure nonce
    nonce = secrets.token_hex(32)  # Increased entropy
    
    # Store with expiration (5 minutes)
    session['siwe_nonce'] = nonce
    session['siwe_address'] = address
    session['nonce_timestamp'] = datetime.now().timestamp()
    session[rate_limit_key] = requests_count + 1
    
    return jsonify({'nonce': nonce})

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    # Rate limiting check
    client_ip = request.remote_addr
    auth_limit_key = f"auth_attempts_{client_ip}"
    auth_attempts = session.get(auth_limit_key, 0)
    
    if auth_attempts >= 5:  # Max 5 auth attempts per session
        return jsonify({'success': False, 'message': 'Too many authentication attempts'}), 429
    
    # Validate request content type
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid content type'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    address = data.get('address', '').strip().lower()
    signature = data.get('signature', '').strip()
    nonce = data.get('nonce', '').strip()
    
    expected_nonce = session.get('siwe_nonce')
    expected_address = session.get('siwe_address')
    nonce_timestamp = session.get('nonce_timestamp')
    
    # Increment auth attempts
    session[auth_limit_key] = auth_attempts + 1
    
    # Validate all required fields
    if not all([address, signature, nonce, expected_nonce, expected_address]):
        return jsonify({'success': False, 'message': 'Missing required authentication data'}), 400
    
    # Check nonce expiration (5 minutes)
    if nonce_timestamp and (datetime.now().timestamp() - nonce_timestamp) > 300:
        session.pop('siwe_nonce', None)
        session.pop('siwe_address', None)
        session.pop('nonce_timestamp', None)
        return jsonify({'success': False, 'message': 'Authentication nonce expired'}), 400
    
    # Validate nonce and address match
    if nonce != expected_nonce or address != expected_address:
        return jsonify({'success': False, 'message': 'Authentication data mismatch'}), 400
    
    # Enhanced address validation
    if not address.startswith('0x') or len(address) != 42:
        return jsonify({'success': False, 'message': 'Invalid address format'}), 400
    
    try:
        int(address[2:], 16)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid address characters'}), 400
    
    # Verify signature with enhanced error handling
    try:
        w3 = Web3()
        message = f'Sign this message to login: {nonce}'
        
        # Additional signature validation
        if not signature.startswith('0x') or len(signature) != 132:
            raise ValueError('Invalid signature format')
        
        recovered = w3.eth.account.recover_message(text=message, signature=signature)
        
    except Exception as e:
        logging.error(f"Signature verification error: {str(e)}")
        return jsonify({'success': False, 'message': 'Signature verification failed'}), 400
    
    if recovered.lower() != address:
        return jsonify({'success': False, 'message': 'Signature verification failed - address mismatch'}), 400
    
    # Success: log in user and clear session data
    session['wallet_address'] = address
    session.pop('siwe_nonce', None)
    session.pop('siwe_address', None)
    session.pop('nonce_timestamp', None)
    session.pop(auth_limit_key, None)  # Clear auth attempts on success
    
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
