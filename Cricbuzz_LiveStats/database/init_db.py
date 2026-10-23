
from db_manager import initialize_database, get_table_counts

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
    print("Current table counts:", get_table_counts())
