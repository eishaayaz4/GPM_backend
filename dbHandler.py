from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

class DBHandler:
    Base = declarative_base()

    def __init__(self, server, database, trusted_connection=False, username=None, password=None):
        if trusted_connection:
            connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        else:
            connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

        self.engine = create_engine(connection_string, echo=True)
        self.Session = sessionmaker(bind=self.engine)

def return_session():
    server = 'DESKTOP-HU3G8O9\\SQLEXPRESS'  # Double backslashes for escaping
    database = 'GPM'
    trusted_connection = False  # Use SQL Server Authentication
    username = 'sa'
    password = '12345678'
    db_handler = DBHandler(server=server, database=database, trusted_connection=trusted_connection, username=username, password=password)
    return db_handler.Session()

def check_database_connection():
    try:
        server = r'DESKTOP-HU3G8O9\\SQLEXPRESS'
        database = 'GPM'
        trusted_connection = False  # Use SQL Server Authentication
        username = 'sa'
        password = '12345678'
        db_handler = DBHandler(server=server, database=database, trusted_connection=trusted_connection, username=username, password=password)
        db_handler.engine.connect()
        print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        exit()