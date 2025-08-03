from datetime import datetime
import sqlite3
import threading
from typing import Optional, Dict, Any

class URLShortenerDB:
    """Database manager for URL shortener service"""
    
    def __init__(self, db_path: str = "url_shortener.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with required tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    short_code TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    click_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def create_url_mapping(self, short_code: str, original_url: str) -> bool:
        """Create a new URL mapping"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
                    (short_code, original_url)
                )
                
                conn.commit()
                conn.close()
                return True
        except sqlite3.IntegrityError:
            # Short code already exists
            return False
        except Exception:
            return False
    
    def get_url_mapping(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get URL mapping by short code"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT short_code, original_url, created_at, click_count FROM urls WHERE short_code = ?',
                    (short_code,)
                )
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {
                        'short_code': result[0],
                        'original_url': result[1],
                        'created_at': result[2],
                        'click_count': result[3]
                    }
                return None
        except Exception:
            return None
    
    def increment_click_count(self, short_code: str) -> bool:
        """Increment click count for a URL"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?',
                    (short_code,)
                )
                
                conn.commit()
                conn.close()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def get_all_urls(self) -> list:
        """Get all URL mappings (for testing/debugging)"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT short_code, original_url, created_at, click_count FROM urls'
                )
                
                results = cursor.fetchall()
                conn.close()
                
                return [
                    {
                        'short_code': row[0],
                        'original_url': row[1],
                        'created_at': row[2],
                        'click_count': row[3]
                    }
                    for row in results
                ]
        except Exception:
            return []
    
    def delete_url(self, short_code: str) -> bool:
        """Delete a URL mapping (for testing/debugging)"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM urls WHERE short_code = ?', (short_code,))
                
                conn.commit()
                conn.close()
                return cursor.rowcount > 0
        except Exception:
            return False

# Global database instance
db = URLShortenerDB()