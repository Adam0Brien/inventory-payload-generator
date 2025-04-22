from setuptools import setup, find_packages

setup(
    name="invgen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["jsonref", "PyYAML", "requests", "faker"],
    entry_points={
    "console_scripts": [
        "invgen = invgen.cli:main"
        ]
    },
)
