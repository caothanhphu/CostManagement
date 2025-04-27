import psycopg2
from dotenv import load_dotenv
import os

def test_db_connection():
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve database connection parameters
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    # Validate that all parameters are present
    if not all([db_host, db_port, db_name, db_user, db_password]):
        print("Error: Missing one or more database connection parameters in .env file")
        print(f"DB_HOST: {db_host}")
        print(f"DB_PORT: {db_port}")
        print(f"DB_NAME: {db_name}")
        print(f"DB_USER: {db_user}")
        print(f"DB_PASSWORD: {'****' if db_password else None}")
        return

    # Construct connection string
    conn_string = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"

    try:
        # Attempt to connect to the database
        print(f"Attempting to connect to database: {db_name} at {db_host}:{db_port}")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Execute a simple query to verify connection
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print("Connection successful!")
        print(f"PostgreSQL version: {db_version}")

        # Check if the Users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'Users'
            );
        """)
        users_table_exists = cursor.fetchone()[0]
        print(f"Users table exists: {users_table_exists}")

        # If the table exists, list its columns
        if users_table_exists:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'Users';
            """)
            columns = cursor.fetchall()
            print("Users table columns:")
            for column in columns:
                print(f"  - {column[0]} ({column[1]})")

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Clean up
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    test_db_connection()