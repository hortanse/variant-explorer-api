"""
Tests for the output formatter module.
"""

import io
import json
import pandas as pd
import pytest
from variant_explorer.formatter import OutputFormatter


class TestOutputFormatter:
    """Test cases for the OutputFormatter class."""
    
    def test_format_gene_data_basic(self):
        """Test basic gene data formatting."""
        # Input data
        gene_info = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1",
            "description": "BRCA1 DNA repair associated",
            "seq_region_name": "17",
            "start": 43044295,
            "end": 43125483,
            "biotype": "protein_coding"
        }
        
        # Call the method
        result = OutputFormatter.format_gene_data(gene_info)
        
        # Check results
        assert result["gene_symbol"] == "BRCA1"
        assert result["gene_id"] == "ENSG00000012048"
        assert result["description"] == "BRCA1 DNA repair associated"
        assert result["location"] == "17:43044295-43125483"
        assert result["biotype"] == "protein_coding"
    
    def test_format_gene_data_with_function(self):
        """Test gene data formatting with function information."""
        # Input data
        gene_info = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1"
        }
        
        gene_function = [
            {
                "dbname": "GO",
                "primary_id": "GO:0006281",
                "description": "DNA repair"
            },
            {
                "dbname": "GO",
                "primary_id": "GO:0051276",
                "description": "chromosome organization"
            },
            {
                "dbname": "UniProt",  # Non-GO entry should be ignored
                "primary_id": "P38398",
                "description": "BRCA1_HUMAN"
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_gene_data(gene_info, gene_function)
        
        # Check results
        assert result["function"] == "DNA repair, chromosome organization"
    
    def test_format_gene_data_with_pathways(self):
        """Test gene data formatting with pathway information."""
        # Input data
        gene_info = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1"
        }
        
        gene_pathways = [
            {
                "dbname": "Reactome",
                "primary_id": "R-HSA-5693567",
                "description": "HDR through Homologous Recombination (HRR)"
            },
            {
                "dbname": "KEGG",
                "primary_id": "hsa03440",
                "description": "Homologous recombination"
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_gene_data(gene_info, gene_pathways=gene_pathways)
        
        # Check results
        assert result["pathways"] == "HDR through Homologous Recombination (HRR), Homologous recombination"
    
    def test_format_gene_data_with_transcripts(self):
        """Test gene data formatting with transcript information."""
        # Input data
        gene_info = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1",
            "Transcript": [
                {
                    "id": "ENST00000357654",
                    "display_name": "BRCA1-201",
                    "biotype": "protein_coding",
                    "is_canonical": True
                },
                {
                    "id": "ENST00000471181",
                    "display_name": "BRCA1-202",
                    "biotype": "processed_transcript",
                    "is_canonical": False
                }
            ]
        }
        
        # Call the method
        result = OutputFormatter.format_gene_data(gene_info, include_transcripts=True)
        
        # Check results
        assert "transcripts" in result
        assert len(result["transcripts"]) == 2
        assert result["transcripts"][0]["transcript_id"] == "ENST00000357654"
        assert result["transcripts"][0]["is_canonical"] is True
        assert result["transcripts"][1]["transcript_id"] == "ENST00000471181"
    
    def test_format_gene_data_with_phenotypes(self):
        """Test gene data formatting with phenotype information."""
        # Input data
        gene_info = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1"
        }
        
        phenotypes = [
            {
                "source": {
                    "name": "OMIM",
                    "url": "https://omim.org/entry/113705"
                },
                "phenotype": {
                    "description": "Breast-ovarian cancer, familial 1"
                }
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_gene_data(gene_info, include_phenotypes=phenotypes)
        
        # Check results
        assert "phenotypes" in result
        assert len(result["phenotypes"]) == 1
        assert result["phenotypes"][0]["description"] == "Breast-ovarian cancer, familial 1"
        assert result["phenotypes"][0]["source"] == "OMIM"
    
    def test_format_variant_data_basic(self):
        """Test basic variant data formatting."""
        # Input data
        variant_info = [
            {
                "id": "rs80357906",
                "seq_region_name": "17",
                "start": 41245466,
                "allele_string": "G/A",
                "most_severe_consequence": "missense_variant"
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_variant_data(variant_info)
        
        # Check results
        assert result["variant_id"] == "rs80357906"
        assert result["location"] == "17:41245466"
        assert result["reference"] == "G"
        assert result["alternate"] == "A"
        assert result["variant_effect"] == "missense_variant"
    
    def test_format_variant_data_with_consequences(self):
        """Test variant data formatting with consequence information."""
        # Input data
        variant_info = [
            {
                "id": "rs80357906",
                "seq_region_name": "17",
                "start": 41245466,
                "allele_string": "G/A",
                "most_severe_consequence": "missense_variant",
                "transcript_consequences": [
                    {
                        "amino_acids": "R/Q",
                        "protein_start": 1699
                    }
                ]
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_variant_data(variant_info)
        
        # Check results
        assert result["consequence"] == "p.RtoQ1699"
    
    def test_format_variant_data_with_clinical_significance(self):
        """Test variant data formatting with clinical significance."""
        # Input data
        variant_info = [
            {
                "id": "rs80357906",
                "seq_region_name": "17",
                "start": 41245466,
                "allele_string": "G/A",
                "most_severe_consequence": "missense_variant",
                "clinical_significance": ["pathogenic", "drug_response"]
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_variant_data(variant_info)
        
        # Check results
        assert result["clinical_significance"] == "pathogenic, drug_response"
    
    def test_format_variant_data_with_frequencies(self):
        """Test variant data formatting with frequency information."""
        # Input data
        variant_info = [
            {
                "id": "rs80357906",
                "seq_region_name": "17",
                "start": 41245466,
                "allele_string": "G/A",
                "colocated_variants": [
                    {
                        "frequencies": {
                            "gnomAD": {
                                "A": 0.00032
                            },
                            "1000GENOMES": {
                                "A": 0.0002
                            }
                        }
                    }
                ]
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_variant_data(variant_info)
        
        # Check results
        assert result["global_frequency"] == 0.00032
    
    def test_format_variant_data_with_population_data(self):
        """Test variant data formatting with detailed population data."""
        # Input data
        variant_info = [
            {
                "id": "rs80357906",
                "seq_region_name": "17",
                "start": 41245466,
                "allele_string": "G/A",
                "colocated_variants": [
                    {
                        "frequencies": {
                            "gnomAD": {
                                "A": 0.00032,
                                "afr": 0.0001,
                                "eur": 0.0005
                            }
                        }
                    }
                ]
            }
        ]
        
        # Call the method
        result = OutputFormatter.format_variant_data(variant_info, include_populations=True)
        
        # Check results
        assert "population_frequencies" in result
        assert result["population_frequencies"]["gnomAD"]["A"] == 0.00032
        assert result["population_frequencies"]["gnomAD"]["afr"] == 0.0001
        assert result["population_frequencies"]["gnomAD"]["eur"] == 0.0005
    
    def test_to_csv(self):
        """Test CSV output formatting."""
        # Input data
        data = [
            {
                "gene_symbol": "BRCA1",
                "gene_id": "ENSG00000012048",
                "description": "BRCA1 DNA repair associated",
                "function": "DNA repair"
            },
            {
                "gene_symbol": "TP53",
                "gene_id": "ENSG00000141510",
                "description": "tumor protein p53",
                "function": "DNA damage response"
            }
        ]
        
        # Call the method
        output = io.StringIO()
        OutputFormatter.to_csv(data, output)
        output.seek(0)
        
        # Check results
        df = pd.read_csv(output)
        assert len(df) == 2
        assert list(df.columns) == ["gene_symbol", "gene_id", "description", "function"]
        assert df.iloc[0]["gene_symbol"] == "BRCA1"
        assert df.iloc[1]["gene_symbol"] == "TP53"
    
    def test_to_csv_with_nested_data(self):
        """Test CSV output formatting with nested dictionaries."""
        # Input data
        data = [
            {
                "gene_symbol": "BRCA1",
                "transcripts": [
                    {"id": "ENST00000357654", "name": "BRCA1-201"}
                ]
            }
        ]
        
        # Call the method
        output = io.StringIO()
        OutputFormatter.to_csv(data, output)
        output.seek(0)
        
        # Check results
        df = pd.read_csv(output)
        assert len(df) == 1
        assert "transcripts" in df.columns
        assert isinstance(df.iloc[0]["transcripts"], str)
        
        # Check that the nested data was properly JSON-encoded
        transcripts = json.loads(df.iloc[0]["transcripts"])
        assert isinstance(transcripts, list)
        assert transcripts[0]["id"] == "ENST00000357654"
    
    def test_to_json(self):
        """Test JSON output formatting."""
        # Input data
        data = {
            "gene_symbol": "BRCA1",
            "gene_id": "ENSG00000012048",
            "nested": {
                "key": "value"
            }
        }
        
        # Call the method
        output = io.StringIO()
        OutputFormatter.to_json(data, output)
        output.seek(0)
        
        # Check results
        result = json.loads(output.read())
        assert result["gene_symbol"] == "BRCA1"
        assert result["gene_id"] == "ENSG00000012048"
        assert result["nested"]["key"] == "value" 