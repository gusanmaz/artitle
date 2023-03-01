from setuptools import setup, find_packages

setup(
    name='artitle',
    version='0.0.1',
    packages=find_packages(include=['src', 'src.*']),
    package_data={
        "src": ["config.json"]
    },
    install_requires=[
        'requests',
        'argparse',
    ],
    setup_requires=[
        'setuptools>=40.8.0',
        'wheel>=0.33.1'
    ],
    entry_points={
        'console_scripts': [
            'artitle = src.main:main'
        ]
    }
)
