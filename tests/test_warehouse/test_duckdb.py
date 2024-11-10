# tests/test_warehouse/test_duckdb.py
from crypto_pipeline.crypto_pipeline.warehouse.duckdb.init_db import DuckDBManager
from unittest.mock import Mock
import pytest

@pytest.fixture
def db_manager():
    """fixture to create a test DuckDBManager with mocked AWS creds"""
    manager = DuckDBManager(':memory:')
    manager.credentials = Mock(access_key='test', secret_key='test')
    manager.region = 'us-east-1'
    yield manager

def test_aws_configuration(db_manager):
    """test that AWS creds are correctly aligned"""
    with db_manager.get_connection() as conn:
        settings = conn.execute("""
            SELECT
                current_setting('s3_region'),
                current_setting('s3_access_key_id'),
                current_setting('s3_secret_access_key')
        """).fetchone()

        assert settings[0] == 'us-east-1'
        assert settings[1] == 'test'
        assert settings[2] == 'test'

def test_connection_lifecycle(db_manager):
    """test connection, execution"""
    with db_manager.get_connection() as conn:
        result = conn.execute('SELECT 1').fetchall()
        assert result == [(1,)]

def test_connection_cleanup(db_manager):
    """test connection closure after error"""
    # cause an error
    try:
        with db_manager.get_connection() as conn:
            raise Exception("Panic!!")
    except Exception:
        pass

    # try to reconnect after closure
    with db_manager.get_connection() as conn:
        result = conn.execute('SELECT 1').fetchall()
        assert result == [(1,)]
