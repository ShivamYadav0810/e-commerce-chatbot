import sqlite3
import logging
from typing import List, Dict, Any, Optional
from config import SQLITE_DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, recreate: bool = False):
        self.db_path = SQLITE_DB_PATH
        self.recreate = recreate
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database with sample order data"""
        try:
            if self.recreate:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Create orders table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        customer_name TEXT NOT NULL,
                        customer_email TEXT NOT NULL,
                        product_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        total_amount REAL NOT NULL,
                        order_date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        tracking_number TEXT,
                        estimated_delivery TEXT
                    )
                """)
                
                # Sample order data
                sample_orders = [
                    ("ABC-123", "John Doe", "john@email.com", "Wireless Headphones", 1, 99.99, "2025-08-14", "shipped", "TRK123456789", "2025-08-29"),
                    ("XYZ-456", "Jane Smith", "jane@email.com", "Smartphone Case", 2, 29.98, "2025-08-25", "processing", None, "2025-09-04"),
                    ("DEF-789", "Mike Johnson", "mike@email.com", "Gaming Mouse", 1, 79.99, "2025-07-17", "delivered", "TRK987654321", "2025-08-19"),
                    ("GHI-012", "Sarah Wilson", "sarah@email.com", "USB Cable", 3, 23.97, "2025-08-18", "shipped", "TRK456789123", "2025-08-31"),
                    ("JKL-345", "Bob Brown", "bob@email.com", "Bluetooth Speaker", 1, 149.99, "2025-08-24", "processing", None, "2025-09-07"),
                    ("MNO-678", "Lisa Davis", "lisa@email.com", "Laptop Stand", 1, 59.99, "2025-05-20", "cancelled", None, None),
                    ("PQR-901", "Tom Anderson", "tom@email.com", "Phone Charger", 2, 39.98, "2025-08-15", "shipped", "TRK789123456", "2025-09-01"),
                    ("STU-234", "Amy Taylor", "amy@email.com", "Tablet Screen Protector", 1, 12.99, "2025-07-22", "delivered", "TRK321654987", "2025-08-20"),
                ]
                
                # Insert sample data
                cursor.executemany("""
                    INSERT OR REPLACE INTO orders 
                    (order_id, customer_name, customer_email, product_name, quantity, total_amount, 
                    order_date, status, tracking_number, estimated_delivery)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_orders)
                
                conn.commit()
                conn.close()
                logger.info("Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """Get the status of an order by order_id"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    