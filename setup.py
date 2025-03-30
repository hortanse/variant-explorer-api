from setuptools import setup, find_packages

setup(
    name="variant-explorer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.1.0",
        "colorama>=0.4.4",
        "tqdm>=4.50.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
            "isort>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "variant-explorer=variant_explorer.main:main",
        ],
    },
    author="Yi-Fan Chou",
    author_email="hortanse@egmail.com",
    description="A CLI tool for retrieving gene and variant information from Ensembl REST API",
    keywords="bioinformatics, genomics, ensembl, variant, gene",
    url="https://github.com/hortanse/variant-explorer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
) 