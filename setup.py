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
        'dbt-core',
        'dbt-duckdb'
    ]
)