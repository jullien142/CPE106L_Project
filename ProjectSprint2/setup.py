from setuptools import setup, find_packages

setup(
    name="community_skill_exchange",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flet>=0.7.0",
        "SQLAlchemy>=1.4",
        "matplotlib>=3.5",
    ],
    entry_points={
        'console_scripts': [
            'community_skill_exchange=community_skill_exchange.main:main',
        ],
    },
) 