"""
Command-line interface for the Variant Explorer tool.
"""

import argparse
import sys
from typing import List, Optional


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:]).
        
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Variant Explorer - A CLI tool for retrieving gene and variant information from Ensembl REST API",
        prog="variant-explorer"
    )
    
    # Add subparsers for 'gene' and 'variant' commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True
    
    # Gene query command
    gene_parser = subparsers.add_parser("gene", help="Query gene information")
    gene_parser.add_argument("symbols", nargs="+", help="Gene symbol(s) to query")
    gene_parser.add_argument(
        "--species", 
        default="human", 
        help="Species (default: human)"
    )
    gene_parser.add_argument(
        "--include-transcripts", 
        action="store_true", 
        help="Include transcript information"
    )
    gene_parser.add_argument(
        "--include-phenotypes", 
        action="store_true", 
        help="Include phenotype associations"
    )
    
    # Variant query command
    variant_parser = subparsers.add_parser("variant", help="Query variant information")
    variant_parser.add_argument("variants", nargs="+", help="Variant(s) to query in format chr:position:ref:alt")
    variant_parser.add_argument(
        "--assembly", 
        default="GRCh38", 
        choices=["GRCh37", "GRCh38"], 
        help="Genome assembly (default: GRCh38)"
    )
    variant_parser.add_argument(
        "--include-populations", 
        action="store_true", 
        help="Include all population frequencies"
    )
    
    # General options (add to both subparsers)
    for subparser in [gene_parser, variant_parser]:
        subparser.add_argument(
            "-o", "--output", 
            type=str, 
            help="Output file path for results (default: stdout)"
        )
        subparser.add_argument(
            "-f", "--format", 
            choices=["csv", "json"], 
            default="csv", 
            help="Output format: csv or json (default: csv)"
        )
        subparser.add_argument(
            "-v", "--verbose", 
            action="store_true", 
            help="Enable verbose output"
        )
        subparser.add_argument(
            "--fields", 
            type=str, 
            help="Comma-separated list of fields to include in output"
        )
    
    return parser.parse_args(args) 