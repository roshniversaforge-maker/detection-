import pymysql
import sys
import os

# Add parent directory to path so we can import from database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_config import get_db_connection

def init_database():
    """
    Creates the main database and necessary tables if they don't exist.
    """
    # Initially connect without database selected to create the database if needed
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='simplepass123',
            autocommit=True
        )
        with connection.cursor() as cursor:
            print("Creating database fakedetection_db if it doesn't exist...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS fakedetection_db;")
        connection.close()
    except Exception as e:
        print(f"Failed to connect to MySQL server. Is it running? Error: {e}")
        return

    # Now connect with the database to create tables
    conn = get_db_connection()
    if not conn:
        print("Failed to get connection for table creation.")
        return

    try:
        with conn.cursor() as cursor:
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

            print("Creating reviews table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_url VARCHAR(500) NOT NULL,
                    review_text TEXT NOT NULL,
                    prediction VARCHAR(50) NOT NULL,
                    sentiment VARCHAR(50) NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            print("Database initialization successful!")
    except Exception as e:
        print(f"Error initializing DB tables: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
