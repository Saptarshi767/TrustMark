"""
Database models for TrustMark application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy with no app yet
db = SQLAlchemy()

class FlaggedTransaction(db.Model):
    """Model for storing flagged transactions"""
    __tablename__ = 'flagged_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(66), unique=True, nullable=False)
    wallet_address = db.Column(db.String(42), nullable=False)
    reason = db.Column(db.String(50), nullable=False, default='suspicious')
    amount = db.Column(db.Float, nullable=True)
    direction = db.Column(db.String(10), nullable=True)
    note = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FlaggedTransaction {self.tx_hash}>'
    
    def to_dict(self):
        """Convert instance to dictionary"""
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'wallet_address': self.wallet_address,
            'reason': self.reason,
            'amount': self.amount,
            'direction': self.direction,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }