import os
import boto3
import duckdb
from contextlib import contextmanager

class DuckDBManager:
    def __init__(self, db_path=None):
        if db_path is None:
            HOME = os.path.expanduser('~')
            db_path = os.path.join(HOME, 'crypto_pipeline/crypto_trading.duckdb')
        self.db_path = os.path.abspath(db_path)

        # set aws credentials
        session = boto3.Session()
        self.credentials = session.get_credentials()
        self.region = session.region_name

    def _setup_connection(self, conn):
        """setup duckdb connection with extensions and AWS config"""
        # load aws extensions
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        conn.execute("INSTALL aws;")
        conn.execute("LOAD aws;")

        # configure aws
        conn.execute(f"""
            SET s3_region='{self.region}';
            SET s3_access_key_id='{self.credentials.access_key}';
            SET s3_secret_access_key='{self.credentials.secret_key}';
        """)

    def _setup_tables(self, conn):
        """setup external tables & views"""
        # create table `trades` with full reload
        try:
            conn.execute("DROP TABLE IF EXISTS trades")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades AS 
                SELECT
                    *,
                    -- extract partition info from filepath
                    cast(regexp_extract(filename, '/(\d{4})/', 1) as INTEGER) as year,
                    cast(regexp_extract(filename, '/(\d{2})/', 1) as INTEGER) as month,
                    cast(regexp_extract(filename, '/(\d{2})/[^/]+$', 1) as INTEGER) as day
                FROM read_csv_auto(
                    's3://crypto-pipeline-dev-data/raw/trades/*/*/*/btc-usdt_trades.csv',
                    filename=true
                );
            """)
        except Exception as e:
            print(f"Error setting up table trades: {str(e)}")
            raise

    @contextmanager
    def get_connection(self, setup_tables=True):
        """
        create a duckdb connection with optional table setup
        args:
            setup_tables (bool): create external tables
        """
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            self._setup_connection(conn)
            if setup_tables:
                self._setup_tables(conn)
            yield conn
        except Exception as e:
            print(f"Error in connection: {str(e)}")
            raise
        finally:
            if conn:
                try:
                    conn.commit()  
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {str(e)}")
                    raise

        

            