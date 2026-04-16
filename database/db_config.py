import pymysql
import pymysql.cursors

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    Modify credentials here according to your local setup.
    """
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='simplepass123',
            database='fakedetection_db',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None
