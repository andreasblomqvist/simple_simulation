from setuptools import setup, find_packages

setup(
    name="simple-simulation-backend",
    version="0.5.14",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "pytest>=7.0.0",
        "pytest-cov>=3.0.0",
        "python-dotenv>=0.19.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0"
    ]
) 