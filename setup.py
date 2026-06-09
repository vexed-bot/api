from setuptools import setup, find_packages

setup(
    name="vexed",
    version="2.2",
    packages=find_packages(),
    description="The vexed API wrapper",
    url="https://github.com/vexed-bot/api",
    author="vexed-bot",
    install_requires=[
        "discord.py"
    ],
)
