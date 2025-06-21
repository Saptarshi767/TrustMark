# 🛡️ TrustMark - Decentralized Reputation Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Vercel-black.svg)](https://vercel.com)

TrustMark is a decentralized reputation tagging platform that analyzes Ethereum wallet transactions to classify addresses and identify suspicious activities. Built with Flask, it provides a comprehensive web interface and Chrome extension for real-time address reputation checking.

## 🌟 Features

### 🔍 **Transaction Analysis**
- Real-time Ethereum transaction fetching via Etherscan API
- Comprehensive transaction history analysis
- Smart pattern recognition for wallet behavior

### 🏷️ **Address Classification**
Our AI-powered classifier categorizes addresses into:
- **Rookie** - New users with <5 transactions
- **Whale Trader** - High-volume traders (>100,000 ETH)
- **Bot** - Automated trading accounts (>10 contract calls)
- **Hacker** - Addresses with exploit-related transactions
- **Whitehat** - Security researchers and auditors
- **Airdrop Hunter** - Users primarily seeking airdrops
- **Liquidity Provider** - DeFi liquidity providers

### 🚩 **Flagging System**
- Manual transaction flagging with custom reasons
- Community-driven suspicious activity detection
- Real-time flag status updates
- Comprehensive flagging statistics and analytics

### 🌐 **Chrome Extension**
- Real-time Ethereum address detection on any webpage
- Instant reputation badges and warnings
- Seamless integration with the main platform
- Automatic updates of flagged addresses

### 📊 **Dashboard & Analytics**
- Personal transaction dashboard
- Real-time balance checking
- Flagging statistics with charts
- Search functionality for addresses
- Transaction detail views

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- Chrome browser (for extension)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/trustmark.git
   cd trustmark
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "ETHERSCAN_API_KEY=your_etherscan_api_key_here" > .env
   echo "SESSION_SECRET=your_session_secret_here" >> .env
   ```

5. **Initialize the database**
   ```bash
   python -c "from main import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ETHERSCAN_API_KEY` | Etherscan API key for transaction data | Yes | None |
| `SESSION_SECRET` | Flask session secret key | No | `trustmark-dev-secret` |
| `POSTGRES_URL` | PostgreSQL database URL (production) | No | SQLite (local) |

### Getting an Etherscan API Key

1. Visit [Etherscan](https://etherscan.io/apis)
2. Create a free account
3. Generate an API key
4. Add it to your `.env` file

## 📱 Chrome Extension Setup

### Installation

1. **Download the extension**
   - Navigate to `http://localhost:5000`
   - Click "Download Extension"
   - Or manually zip the `chrome_extension/` folder

2. **Install in Chrome**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `chrome_extension/` folder

3. **Configure the extension**
   - Open `chrome_extension/content.js`
   - Replace `BACKEND_URL` with your deployed URL
   - For local development: `http://localhost:5000`

### Usage

- Click the TrustMark extension icon to scan the current page
- Ethereum addresses will be automatically highlighted with reputation badges
- Red badges indicate flagged addresses
- Orange badges indicate suspicious addresses
- Blue badges indicate normal addresses

## 🏗️ Project Structure

```
TrustMark/
├── main.py                 # Flask application entry point
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── vercel.json           # Vercel deployment config
├── utils/
│   ├── classifier.py     # Address classification logic
│   ├── etherscan_api.py  # Etherscan API integration
│   └── blockchain.py     # Blockchain utilities
├── templates/
│   ├── index.html        # Landing page
│   ├── login.html        # Wallet login
│   ├── dashboard.html    # User dashboard
│   ├── search.html       # Address search
│   └── flagged_stats.html # Flagging statistics
├── static/
│   ├── css/style.css     # Custom styles
│   ├── js/script.js      # Frontend JavaScript
│   └── chrome_extension.zip # Extension download
├── chrome_extension/
│   ├── manifest.json     # Extension manifest
│   ├── popup.html        # Extension popup
│   ├── content.js        # Content script
│   └── icons/            # Extension icons
└── instance/
    └── trustmark.db      # SQLite database (local)
```

## 🔌 API Endpoints

### Web Interface
- `GET /` - Landing page
- `GET /login` - Wallet login page
- `POST /login` - Process wallet login
- `GET /dashboard` - User dashboard
- `GET /search` - Address search page
- `GET /flagged_stats` - Flagging statistics

### API Endpoints
- `POST /classify` - Classify address from transaction data
- `POST /flag_tx` - Flag a transaction
- `GET /api/flagged_transactions` - Get user's flagged transactions
- `GET /api/flagged_addresses` - Get all flagged addresses (for extension)
- `GET /api/nonce` - Get authentication nonce
- `POST /api/authenticate` - Authenticate user

## 🎨 UI/UX Features

### Modern Design
- **Glassmorphism** effects with backdrop blur
- **3D animations** and hover effects
- **Dark/Light mode** toggle
- **Responsive design** for all devices
- **AOS animations** for smooth page transitions

### Interactive Elements
- Real-time transaction flagging
- Dynamic address classification
- Interactive charts and statistics
- Smooth navigation and transitions

## 🚀 Deployment

### Vercel Deployment

1. **Connect your repository to Vercel**
2. **Set environment variables** in Vercel dashboard:
   - `ETHERSCAN_API_KEY`
   - `SESSION_SECRET`
   - `POSTGRES_URL` (if using PostgreSQL)

3. **Deploy automatically** on git push

### Other Platforms

The application can be deployed to any platform supporting Python:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## 🧪 Testing

### Manual Testing
1. Start the application locally
2. Navigate to `http://localhost:5000`
3. Test wallet login with a valid Ethereum address
4. Explore dashboard features
5. Test transaction flagging
6. Install and test Chrome extension

### Sample Ethereum Addresses for Testing
- `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6` (Vitalik's address)
- `0x28C6c06298d514Db089934071355E5743bf21d60` (Binance hot wallet)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guide
- Add docstrings to all functions
- Include type hints where appropriate
- Write tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Etherscan** for providing the Ethereum blockchain API
- **Flask** community for the excellent web framework
- **Bootstrap** for the responsive UI components
- **Font Awesome** for the beautiful icons

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/trustmark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/trustmark/discussions)
- **Email**: support@trustmark.dev

## 🔮 Roadmap

- [ ] **Machine Learning Integration** - Enhanced classification algorithms
- [ ] **Multi-chain Support** - Extend to other blockchains
- [ ] **Mobile App** - iOS and Android applications
- [ ] **API Rate Limiting** - Improved API management
- [ ] **Community Features** - User profiles and reputation scores
- [ ] **Advanced Analytics** - More detailed transaction insights
- [ ] **Web3 Integration** - Direct wallet connections
- [ ] **Notification System** - Real-time alerts for flagged addresses

---

**Built with ❤️ for the Ethereum community**

*TrustMark - Enhancing trust in the decentralized ecosystem* 