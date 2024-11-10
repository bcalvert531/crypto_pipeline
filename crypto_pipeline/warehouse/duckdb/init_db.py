import os
import boto3
import duckdb
from contextlib import contextmanager

class DuckDBManager:
    def __init__(self, db_path='crpyto_trading.db'):
        self.db_path = db_path

        # set AWS credentials
        session = boto3.Session()
        self.credentials = session.get_credentials()
        self.region = session.region_name

    def _setup_connection(self, conn):
        """setup duckdb connection with extensions and AWS config"""
        # load extensions
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        conn.execute("INSTALL aws;")
        conn.execute("LOAD aws;")

        # configure AWS
        conn.execute(f"""
            SET s3_region='{self.region}';
            SET s3_access_key_id='{self.credentials.access_key}';
            SET s3_access_secret_key='{self.credentials.secret_key}';
        """)

    @contextmanager
    def get_connection(self):
        conn = duckdb.connect(self.db_path)
        try:
            self._setup_connection(conn)
            yield conn
        finally:
            conn.close()

        

            