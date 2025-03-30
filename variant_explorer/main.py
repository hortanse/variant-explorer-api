"""
Main module for the Variant Explorer tool.
"""

import os
import sys
from typing import List, Dict, TextIO, Optional
import logging
from tqdm import tqdm
from colorama import init, Fore, Style

from variant_explorer.cli import parse_args
from variant_explorer.ensembl_api import EnsemblAPI
from variant_explorer.formatter import OutputFormatter


# Initialize colorama
init()


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose output.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format)


def process_gene_query(
    api: EnsemblAPI,
    symbols: List[str],
    species: str = "human",
    include_transcripts: bool = False,
    include_phenotypes: bool = False,
    verbose: bool = False
) -> List[Dict]:
    """
    Process gene query and return formatted results.
    
    Args:
        api: EnsemblAPI instance.
        symbols: List of gene symbols to query.
        species: Species name.
        include_transcripts: Whether to include transcript information.
        include_phenotypes: Whether to include phenotype associations.
        verbose: Whether to enable verbose output.
        
    Returns:
        List of formatted gene data.
    """
    results = []
    
    with tqdm(total=len(symbols), disable=not verbose) as pbar:
        for symbol in symbols:
            try:
                pbar.set_description(f"Processing gene {symbol}")
                
                # Get gene information
                gene_info = api.get_gene_info(symbol, species)
                
                # Get gene function
                gene_function = api.get_gene_function(gene_info["id"])
                
                # Get pathway information
                gene_pathways = api.get_gene_pathways(gene_info["id"])
                
                # Get phenotype associations if requested
                phenotypes = None
                if include_phenotypes:
                    phenotypes = api.get_gene_phenotypes(gene_info["id"])
                
                # Format the data
                formatted_data = OutputFormatter.format_gene_data(
                    gene_info=gene_info,
                    gene_function=gene_function,
                    gene_pathways=gene_pathways,
                    include_transcripts=include_transcripts,
                    include_phenotypes=phenotypes
                )
                
                results.append(formatted_data)
            
            except Exception as e:
                logging.error(f"Error processing gene {symbol}: {str(e)}")
                if verbose:
                    logging.exception(e)
            
            pbar.update(1)
    
    return results


def process_variant_query(
    api: EnsemblAPI,
    variants: List[str],
    assembly: str = "GRCh38",
    include_populations: bool = False,
    verbose: bool = False
) -> List[Dict]:
    """
    Process variant query and return formatted results.
    
    Args:
        api: EnsemblAPI instance.
        variants: List of variants to query.
        assembly: Genome assembly version.
        include_populations: Whether to include detailed population frequencies.
        verbose: Whether to enable verbose output.
        
    Returns:
        List of formatted variant data.
    """
    results = []
    
    with tqdm(total=len(variants), disable=not verbose) as pbar:
        for variant in variants:
            try:
                pbar.set_description(f"Processing variant {variant}")
                
                # Get variant information
                variant_info = api.get_variant_info(variant, assembly)
                
                # Format the data
                formatted_data = OutputFormatter.format_variant_data(
                    variant_info=variant_info,
                    include_populations=include_populations
                )
                
                results.append(formatted_data)
            
            except Exception as e:
                logging.error(f"Error processing variant {variant}: {str(e)}")
                if verbose:
                    logging.exception(e)
            
            pbar.update(1)
    
    return results


def filter_fields(data: List[Dict], fields: Optional[str] = None) -> List[Dict]:
    """
    Filter the data to include only the specified fields.
    
    Args:
        data: List of data dictionaries.
        fields: Comma-separated list of fields to include.
        
    Returns:
        Filtered data.
    """
    if not fields:
        return data
    
    field_list = [field.strip() for field in fields.split(",")]
    
    filtered_data = []
    for item in data:
        filtered_item = {field: item.get(field, "") for field in field_list if field in item}
        filtered_data.append(filtered_item)
    
    return filtered_data


def write_output(
    data: List[Dict],
    output_file: Optional[str] = None,
    output_format: str = "csv"
) -> None:
    """
    Write the formatted data to the specified output.
    
    Args:
        data: Data to write.
        output_file: Output file path (or None for stdout).
        output_format: Output format ('csv' or 'json').
    """
    # If there's no data, print an error message
    if not data:
        print(f"{Fore.RED}No results found.{Style.RESET_ALL}", file=sys.stderr)
        return
    
    # Determine output destination
    if output_file:
        with open(output_file, "w") as f:
            if output_format == "csv":
                OutputFormatter.to_csv(data, f)
            else:  # json
                OutputFormatter.to_json(data, f)
        
        print(f"{Fore.GREEN}Results saved to {output_file}{Style.RESET_ALL}")
    else:
        # Output to stdout
        if output_format == "csv":
            OutputFormatter.to_csv(data, sys.stdout)
        else:  # json
            OutputFormatter.to_json(data, sys.stdout)


def main() -> int:
    """
    Main entry point for the CLI tool.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    try:
        # Initialize API client
        api = EnsemblAPI()
        
        # Process the command
        if args.command == "gene":
            # Process gene query
            results = process_gene_query(
                api=api,
                symbols=args.symbols,
                species=args.species,
                include_transcripts=args.include_transcripts,
                include_phenotypes=args.include_phenotypes,
                verbose=args.verbose
            )
        elif args.command == "variant":
            # Process variant query
            results = process_variant_query(
                api=api,
                variants=args.variants,
                assembly=args.assembly,
                include_populations=args.include_populations,
                verbose=args.verbose
            )
        else:
            # This should never happen due to subparsers.required = True
            logging.error(f"Unknown command: {args.command}")
            return 1
        
        # Filter fields if requested
        if args.fields:
            results = filter_fields(results, args.fields)
        
        # Write the output
        write_output(
            data=results,
            output_file=args.output,
            output_format=args.format
        )
        
        return 0
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        if args.verbose:
            logging.exception(e)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 