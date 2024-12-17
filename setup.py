from setuptools import setup, find_packages

setup(
    name="WikiDataPy",
    version="0.0.2",
    description="WikidataPy is a Python library designed for seamless interaction with Wikidata's knowledgebase, enabling users to perform a variety of operations such as searching entities, retrieving claims, performing SPARQL queries, and even visualizing knowledge graphs.",
    author="Aryan Sethi",
    license="MIT",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "requests>=2.32.3",
        "pandas>=1.0.0",
        "networkx>=2.5",
        "matplotlib>=3.9.2",
        "networkx>=3.4.2",
        "numpy>=2.1.3",
        "tabulate>=0.9.0",
        "matplotlib-inline>=0.1.7"
    ]
)
