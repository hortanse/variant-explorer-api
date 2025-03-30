"""
Module for interacting with the Ensembl REST API.
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin


class EnsemblAPI:
    """
    Class for interacting with the Ensembl REST API.
    """
    BASE_URL = "https://rest.ensembl.org/"
    
    def __init__(self, rate_limit: float = 0.1):
        """
        Initialize the EnsemblAPI client.
        
        Args:
            rate_limit: Minimum time (in seconds) between API requests to avoid hitting rate limits.
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Ensembl REST API with proper rate limiting.
        
        Args:
            endpoint: API endpoint to query.
            params: Optional query parameters.
            
        Returns:
            Response data as a dictionary.
            
        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        # Implement rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)
        
        url = urljoin(self.BASE_URL, endpoint)
        response = self.session.get(url, params=params)
        self.last_request_time = time.time()
        
        response.raise_for_status()
        return response.json()
    
    def get_gene_info(self, symbol: str, species: str = "human") -> Dict:
        """
        Get information about a gene by its symbol.
        
        Args:
            symbol: Gene symbol (e.g., 'BRCA1').
            species: Species name (default: 'human').
            
        Returns:
            Dictionary with gene information.
        """
        endpoint = f"lookup/symbol/{species}/{symbol}"
        params = {"expand": 1}
        return self._make_request(endpoint, params)
    
    def get_gene_function(self, gene_id: str) -> Dict:
        """
        Get information about gene function and biological processes.
        
        Args:
            gene_id: Ensembl gene ID (e.g., 'ENSG00000012048').
            
        Returns:
            Dictionary with gene function information.
        """
        endpoint = f"xrefs/id/{gene_id}"
        params = {"external_db": "GO"}
        return self._make_request(endpoint, params)
    
    def get_gene_pathways(self, gene_id: str) -> Dict:
        """
        Get pathway information for a gene.
        
        Args:
            gene_id: Ensembl gene ID (e.g., 'ENSG00000012048').
            
        Returns:
            Dictionary with pathway information.
        """
        endpoint = f"xrefs/id/{gene_id}"
        params = {"external_db": "Reactome,KEGG"}
        return self._make_request(endpoint, params)
    
    def get_gene_phenotypes(self, gene_id: str) -> Dict:
        """
        Get phenotype associations for a gene.
        
        Args:
            gene_id: Ensembl gene ID (e.g., 'ENSG00000012048').
            
        Returns:
            Dictionary with phenotype information.
        """
        endpoint = f"phenotype/gene/{gene_id}"
        return self._make_request(endpoint)
    
    def get_variant_info(self, variant: str, assembly: str = "GRCh38") -> Dict:
        """
        Get information about a variant by its position.
        
        Args:
            variant: Variant in format "chr:position:ref:alt" (e.g., "chr17:41245466:G:A").
            assembly: Genome assembly version (default: 'GRCh38').
            
        Returns:
            Dictionary with variant information.
        """
        # Parse the variant string
        parts = variant.replace("chr", "").split(":")
        chrom, pos = parts[0], parts[1]
        ref, alt = parts[2], parts[3]
        
        region = f"{chrom}:{pos}:{pos}"
        allele = f"{ref}/{alt}"
        
        endpoint = f"vep/human/{assembly}/{region}/{allele}"
        params = {
            "variant_class": 1,
            "regulatory": 1,
            "clinical_significance": 1,
            "af": 1,
            "af_1kg": 1,
            "af_gnomad": 1
        }
        return self._make_request(endpoint, params)
    
    def get_variant_consequences(self, variant: str, assembly: str = "GRCh38") -> Dict:
        """
        Get consequences of a variant.
        
        Args:
            variant: Variant in format "chr:position:ref:alt" (e.g., "chr17:41245466:G:A").
            assembly: Genome assembly version (default: 'GRCh38').
            
        Returns:
            Dictionary with variant consequences.
        """
        # This is usually included in the VEP output, so we can reuse get_variant_info
        return self.get_variant_info(variant, assembly) 