from setuptools import setup, find_packages

setup(
    name="simplesim",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dotenv>=0.19.0"
    ],
    entry_points={
        'console_scripts': [
            'simplesim-backend=backend.main:app',
        ],
    },
    python_requires=">=3.8",
) 