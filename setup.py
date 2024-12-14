# setup.py
from setuptools import setup, find_packages

setup(
    name="emergency-response-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered emergency response coordination system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)