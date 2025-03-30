"""
Module for formatting API responses into different output formats.
"""

import json
import csv
import pandas as pd
from typing import Dict, List, Any, Union, TextIO
import sys


class OutputFormatter:
    """
    Class for formatting API responses into CSV or JSON formats.
    """
    
    @staticmethod
    def format_gene_data(gene_info: Dict, gene_function: Dict = None, 
                         gene_pathways: Dict = None, include_transcripts: bool = False,
                         include_phenotypes: Dict = None) -> Dict:
        """
        Format gene data for output.
        
        Args:
            gene_info: Gene information from Ensembl API.
            gene_function: Gene function information (optional).
            gene_pathways: Gene pathway information (optional).
            include_transcripts: Whether to include transcript information.
            include_phenotypes: Phenotype associations (optional).
            
        Returns:
            Formatted gene data as a dictionary.
        """
        # Base gene information
        result = {
            "gene_symbol": gene_info.get("display_name", ""),
            "gene_id": gene_info.get("id", ""),
            "description": gene_info.get("description", ""),
            "location": f"{gene_info.get('seq_region_name', '')}:{gene_info.get('start', '')}-{gene_info.get('end', '')}",
            "biotype": gene_info.get("biotype", "")
        }
        
        # Add function information if available
        if gene_function:
            go_terms = [term for term in gene_function if term.get("dbname") == "GO"]
            functions = [term.get("description", "") for term in go_terms if term.get("description")]
            result["function"] = ", ".join(functions) if functions else ""
        
        # Add pathway information if available
        if gene_pathways:
            pathways = []
            for pathway in gene_pathways:
                if pathway.get("dbname") in ["Reactome", "KEGG"] and pathway.get("description"):
                    pathways.append(pathway.get("description"))
            result["pathways"] = ", ".join(pathways) if pathways else ""
        
        # Add transcript information if requested
        if include_transcripts and "Transcript" in gene_info:
            result["transcripts"] = [
                {
                    "transcript_id": transcript.get("id", ""),
                    "transcript_name": transcript.get("display_name", ""),
                    "biotype": transcript.get("biotype", ""),
                    "is_canonical": transcript.get("is_canonical", False)
                }
                for transcript in gene_info.get("Transcript", [])
            ]
        
        # Add phenotype information if available
        if include_phenotypes:
            phenotype_list = []
            for pheno in include_phenotypes:
                if pheno.get("phenotype", {}).get("description"):
                    phenotype_list.append({
                        "description": pheno.get("phenotype", {}).get("description", ""),
                        "source": pheno.get("source", {}).get("name", "")
                    })
            result["phenotypes"] = phenotype_list
        
        return result
    
    @staticmethod
    def format_variant_data(variant_info: Dict, include_populations: bool = False) -> Dict:
        """
        Format variant data for output.
        
        Args:
            variant_info: Variant information from Ensembl API.
            include_populations: Whether to include detailed population frequencies.
            
        Returns:
            Formatted variant data as a dictionary.
        """
        # The variant info from VEP usually has a list of transcripts
        if not variant_info or not isinstance(variant_info, list):
            return {}
        
        # Get the first transcript (most severe consequences are usually listed first)
        first_variant = variant_info[0]
        
        result = {
            "variant_id": first_variant.get("id", ""),
            "location": f"{first_variant.get('seq_region_name', '')}:{first_variant.get('start', '')}",
            "reference": first_variant.get('allele_string', '').split('/')[0],
            "alternate": first_variant.get('allele_string', '').split('/')[1],
            "variant_effect": first_variant.get("most_severe_consequence", ""),
        }
        
        # Add consequence details if available
        if "transcript_consequences" in first_variant:
            consequences = first_variant["transcript_consequences"]
            if consequences:
                first_consequence = consequences[0]
                
                # Add protein consequence if available
                if "protein_start" in first_consequence and "amino_acids" in first_consequence:
                    aa_change = first_consequence.get("amino_acids", "").replace("/", "to")
                    pos = first_consequence.get("protein_start", "")
                    result["consequence"] = f"p.{aa_change}{pos}"
        
        # Add clinical significance if available
        if "clinical_significance" in first_variant:
            result["clinical_significance"] = ", ".join(first_variant["clinical_significance"])
        
        # Add global frequency if available
        if "colocated_variants" in first_variant:
            for colocated in first_variant["colocated_variants"]:
                if "frequencies" in colocated:
                    # Get global frequency from gnomAD if available
                    if "gnomAD" in colocated.get("frequencies", {}):
                        gnomad = colocated["frequencies"]["gnomAD"]
                        alt = result["alternate"]
                        result["global_frequency"] = gnomad.get(alt, "")
                    # Fallback to 1000 Genomes
                    elif "1000GENOMES" in colocated.get("frequencies", {}):
                        genomes_1k = colocated["frequencies"]["1000GENOMES"]
                        alt = result["alternate"]
                        result["global_frequency"] = genomes_1k.get(alt, "")
        
        # Add detailed population frequencies if requested
        if include_populations and "colocated_variants" in first_variant:
            population_data = {}
            for colocated in first_variant["colocated_variants"]:
                if "frequencies" in colocated:
                    for source, freqs in colocated["frequencies"].items():
                        if source not in population_data:
                            population_data[source] = {}
                        for pop, freq in freqs.items():
                            population_data[source][pop] = freq
            
            if population_data:
                result["population_frequencies"] = population_data
        
        return result
    
    @staticmethod
    def to_csv(data: Union[Dict, List[Dict]], output: TextIO = sys.stdout) -> None:
        """
        Format data as CSV and write to the specified output.
        
        Args:
            data: Data to format (dict or list of dicts).
            output: Output file or sys.stdout.
        """
        if not data:
            return
        
        # Convert to list if it's a single dict
        if isinstance(data, dict):
            data_list = [data]
        else:
            data_list = data
        
        # Flatten any nested dictionaries/lists
        flattened_data = []
        for item in data_list:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    flat_item[key] = json.dumps(value)
                else:
                    flat_item[key] = value
            flattened_data.append(flat_item)
        
        # Write data as CSV
        df = pd.DataFrame(flattened_data)
        df.to_csv(output, index=False, quoting=csv.QUOTE_NONNUMERIC)
    
    @staticmethod
    def to_json(data: Union[Dict, List[Dict]], output: TextIO = sys.stdout) -> None:
        """
        Format data as JSON and write to the specified output.
        
        Args:
            data: Data to format (dict or list of dicts).
            output: Output file or sys.stdout.
        """
        json.dump(data, output, indent=2) 