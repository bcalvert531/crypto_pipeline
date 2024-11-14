# crypto_pipeline/setup.py
from setuptools import setup, find_packages

setup(
    name="crypto_pipeline",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),  # Make sure this line is exactly like this
    install_requires=[
        'boto3',
        'duckdb',
        's3fs',
        'dbt-core==1.8.8',
        'dbt-duckdb==1.9.0',
        'protobuf>=4.21.0,<5.0'
        'apache-airflow',
        'apache-superset'
    ]
)