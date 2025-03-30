# Variant Explorer

A Python-based command-line tool for retrieving detailed information about genes and genetic variants using the Ensembl REST API.

## Overview

Variant Explorer is a powerful CLI tool that allows researchers and bioinformaticians to quickly access comprehensive information about genes and variants directly from the Ensembl database. The tool supports queries by gene symbol or variant position and returns detailed biological information in convenient CSV or JSON formats.

## Features

- **Query by Gene Symbol**: Retrieve comprehensive gene information using official gene symbols (e.g., BRCA1, TP53)
- **Query by Variant Position**: Lookup variant details using genomic coordinates (chromosome, position, reference, and alternate alleles)
- **Detailed Information Retrieval**:
  - Gene information (name, ID, description, location)
  - Gene function and biological processes
  - Associated pathways
  - Variant effects and consequences
  - Clinical significance and relevance
  - Population frequency data across multiple databases
- **Output Formats**: Save results in CSV or JSON formats for further analysis or integration with other tools
- **Batch Processing**: Process multiple genes or variants in a single run
- **Configurable Output**: Customize which fields to include in the output

## Requirements

- Python 3.8 or higher
- Required Python packages (will be installed automatically):
  - requests
  - argparse
  - pandas
  - colorama
  - tqdm

## Installation

```bash
# Clone the repository
git clone https://github.com/username/variant-explorer.git
cd variant-explorer

# Install the package
pip install -e .

# Or install directly from PyPI
pip install variant-explorer
```

## Usage

### Basic Usage

```bash
# Query by gene symbol
variant-explorer gene BRCA1

# Query by variant position
variant-explorer variant "chr17:41245466:G:A"

# Save results to file
variant-explorer gene BRCA1 --output results.csv
variant-explorer gene BRCA1 --output results.json --format json

# Query multiple genes
variant-explorer gene BRCA1 TP53 EGFR --output gene_data.csv
```

### Command-line Options

```
General options:
  -h, --help            Show this help message and exit
  -o, --output FILE     Output file path for results (default: stdout)
  -f, --format FORMAT   Output format: csv or json (default: csv)
  -v, --verbose         Enable verbose output
  --fields FIELDS       Comma-separated list of fields to include in output

Gene query options:
  --species SPECIES     Species (default: human)
  --include-transcripts Include transcript information
  --include-phenotypes  Include phenotype associations

Variant query options:
  --assembly ASSEMBLY   Genome assembly: GRCh37 or GRCh38 (default: GRCh38)
  --include-populations Include all population frequencies
```

## Examples

### Example 1: Query information for BRCA1 gene

```bash
variant-explorer gene BRCA1
```

Output (CSV format):
```
gene_symbol,gene_id,description,location,biotype,function,pathways
BRCA1,ENSG00000012048,BRCA1 DNA repair associated,chr17:43044295-43125483,protein_coding,"DNA repair, Cell cycle regulation","Homologous recombination repair, DNA double-strand break repair"
```

### Example 2: Query variant information

```bash
variant-explorer variant "chr17:41245466:G:A"
```

Output (CSV format):
```
variant_id,location,reference,alternate,variant_effect,consequence,clinical_significance,global_frequency
rs80357906,chr17:41245466,G,A,missense_variant,p.Arg1699Gln,Pathogenic,0.00032
```

### Example 3: Save detailed gene information in JSON format

```bash
variant-explorer gene TP53 --include-transcripts --include-phenotypes --format json --output tp53_data.json
```

## API Information

This tool uses the Ensembl REST API (https://rest.ensembl.org/) to retrieve genomic data. The Ensembl REST API provides programmatic access to the Ensembl data using RESTful web services. The tool handles all API interactions transparently, including proper rate limiting and error handling.

Key endpoints used:
- `/lookup/symbol/{species}/{symbol}`: Gene information by symbol
- `/overlap/region/{species}/{region}`: Features (including variants) in a genomic region
- `/vep/{species}/region/{region}/{allele}`: Variant effect predictions

## Data Sources

The information provided by this tool comes from various databases integrated within Ensembl:
- Gene function and pathway data: Gene Ontology (GO), KEGG, Reactome
- Variant consequences: Variant Effect Predictor (VEP)
- Clinical significance: ClinVar, COSMIC
- Population frequencies: gnomAD, 1000 Genomes Project, ExAC

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/username/variant-explorer.git
cd variant-explorer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=variant_explorer

# Run linting
flake8 variant_explorer
```

### Project Structure

```
variant-explorer/
├── variant_explorer/           # Main package
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── ensembl_api.py         # Ensembl API client
│   ├── formatter.py           # Output formatting
│   ├── main.py                # Main entry point
│   └── examples.py            # Usage examples
├── tests/                     # Test directory
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_ensembl_api.py
│   ├── test_formatter.py
│   └── test_main.py
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
├── LICENSE                    # License file
└── README.md                  # This file
```
