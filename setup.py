from setuptools import setup, find_packages

setup(
    name="bungo-writer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-openai",
        "langchain-google-genai",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "bungo-writer=bungo_writer.cli:main",
        ],
    },
)
