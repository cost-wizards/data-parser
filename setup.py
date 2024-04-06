from setuptools import find_packages, setup

setup(
    name="cost_wizard",
    version="0.0.1",
    description="i",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "SQLAlchemy==2.0.29",
        "psycopg2-binary==2.9.9",
        "boto3==1.23.10",
        "botocore==1.26.10",
        "pypika==0.48.9",
        "loguru",
    ],
    python_requires=">=3.9",
)
