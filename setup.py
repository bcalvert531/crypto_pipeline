# crypto-pipeline/setup.py
from setuptools import setup, find_packages

setup(
    name="crypto-pipeline",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'boto3',
        'duckdb',
        's3fs'
    ]
)