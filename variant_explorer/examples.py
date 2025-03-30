"""
Example scripts demonstrating how to use the Variant Explorer API directly.
"""

from variant_explorer.ensembl_api import EnsemblAPI
from variant_explorer.formatter import OutputFormatter
import json


def example_gene_query():
    """
    Example function demonstrating gene query usage.
    """
    # Initialize the API client
    api = EnsemblAPI()
    
    # Get gene information
    gene_symbol = "BRCA1"
    print(f"Getting information for gene {gene_symbol}...")
    
    gene_info = api.get_gene_info(gene_symbol)
    gene_function = api.get_gene_function(gene_info["id"])
    gene_pathways = api.get_gene_pathways(gene_info["id"])
    
    # Format the data
    formatted_data = OutputFormatter.format_gene_data(
        gene_info=gene_info,
        gene_function=gene_function,
        gene_pathways=gene_pathways
    )
    
    # Print the formatted data
    print(json.dumps(formatted_data, indent=2))


def example_variant_query():
    """
    Example function demonstrating variant query usage.
    """
    # Initialize the API client
    api = EnsemblAPI()
    
    # Get variant information
    variant = "chr17:41245466:G:A"
    print(f"Getting information for variant {variant}...")
    
    variant_info = api.get_variant_info(variant)
    
    # Format the data
    formatted_data = OutputFormatter.format_variant_data(
        variant_info=variant_info,
        include_populations=True
    )
    
    # Print the formatted data
    print(json.dumps(formatted_data, indent=2))


if __name__ == "__main__":
    print("Running gene query example:")
    example_gene_query()
    
    print("\nRunning variant query example:")
    example_variant_query() 