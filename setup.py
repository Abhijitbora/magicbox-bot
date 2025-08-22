from setuptools import setup, find_packages

setup(
    name="magicbox-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==13.15",
        "Pillow==10.2.0",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.7",
)
