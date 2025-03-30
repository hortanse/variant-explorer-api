"""
Tests for the Ensembl API client.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from variant_explorer.ensembl_api import EnsemblAPI


class TestEnsemblAPI:
    """Test cases for the EnsemblAPI class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = EnsemblAPI()
    
    @patch('variant_explorer.ensembl_api.requests.Session')
    def test_init(self, mock_session):
        """Test initialization of the API client."""
        api = EnsemblAPI(rate_limit=0.5)
        assert api.rate_limit == 0.5
        assert api.last_request_time == 0
        mock_session.assert_called_once()
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_gene_info(self, mock_make_request):
        """Test retrieving gene information."""
        # Set up mock return value
        mock_make_request.return_value = {
            "id": "ENSG00000012048",
            "display_name": "BRCA1",
            "description": "BRCA1 DNA repair associated",
            "seq_region_name": "17",
            "start": 43044295,
            "end": 43125483,
            "biotype": "protein_coding"
        }
        
        # Call the method
        result = self.api.get_gene_info("BRCA1")
        
        # Check the result
        assert result["id"] == "ENSG00000012048"
        assert result["display_name"] == "BRCA1"
        
        # Check that the method was called with the right arguments
        mock_make_request.assert_called_once_with("lookup/symbol/human/BRCA1", {"expand": 1})
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_gene_function(self, mock_make_request):
        """Test retrieving gene function information."""
        # Set up mock return value
        mock_make_request.return_value = [
            {
                "dbname": "GO",
                "primary_id": "GO:0006281",
                "description": "DNA repair"
            },
            {
                "dbname": "GO",
                "primary_id": "GO:0051276",
                "description": "chromosome organization"
            }
        ]
        
        # Call the method
        result = self.api.get_gene_function("ENSG00000012048")
        
        # Check the result
        assert len(result) == 2
        assert result[0]["dbname"] == "GO"
        assert result[0]["description"] == "DNA repair"
        
        # Check that the method was called with the right arguments
        mock_make_request.assert_called_once_with("xrefs/id/ENSG00000012048", {"external_db": "GO"})
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_gene_pathways(self, mock_make_request):
        """Test retrieving gene pathway information."""
        # Set up mock return value
        mock_make_request.return_value = [
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
        result = self.api.get_gene_pathways("ENSG00000012048")
        
        # Check the result
        assert len(result) == 2
        assert result[0]["dbname"] == "Reactome"
        assert result[1]["dbname"] == "KEGG"
        
        # Check that the method was called with the right arguments
        mock_make_request.assert_called_once_with("xrefs/id/ENSG00000012048", {"external_db": "Reactome,KEGG"})
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_gene_phenotypes(self, mock_make_request):
        """Test retrieving gene phenotype information."""
        # Set up mock return value
        mock_make_request.return_value = [
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
        result = self.api.get_gene_phenotypes("ENSG00000012048")
        
        # Check the result
        assert len(result) == 1
        assert result[0]["source"]["name"] == "OMIM"
        assert result[0]["phenotype"]["description"] == "Breast-ovarian cancer, familial 1"
        
        # Check that the method was called with the right arguments
        mock_make_request.assert_called_once_with("phenotype/gene/ENSG00000012048")
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_variant_info(self, mock_make_request):
        """Test retrieving variant information."""
        # Set up mock return value
        mock_make_request.return_value = [
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
                ],
                "clinical_significance": ["pathogenic"]
            }
        ]
        
        # Call the method
        result = self.api.get_variant_info("chr17:41245466:G:A")
        
        # Check the result
        assert len(result) == 1
        assert result[0]["id"] == "rs80357906"
        assert result[0]["most_severe_consequence"] == "missense_variant"
        
        # Check that the method was called with the right arguments
        mock_make_request.assert_called_once_with(
            "vep/human/GRCh38/17:41245466:41245466/G/A",
            {
                "variant_class": 1,
                "regulatory": 1,
                "clinical_significance": 1,
                "af": 1,
                "af_1kg": 1,
                "af_gnomad": 1
            }
        )
    
    @patch('variant_explorer.ensembl_api.EnsemblAPI._make_request')
    def test_get_variant_consequences(self, mock_make_request):
        """Test retrieving variant consequences."""
        # Set up mock return value
        mock_make_request.return_value = [
            {
                "id": "rs80357906",
                "most_severe_consequence": "missense_variant"
            }
        ]
        
        # Call the method
        result = self.api.get_variant_consequences("chr17:41245466:G:A")
        
        # Check the method was called with the right arguments
        mock_make_request.assert_called_once()
    
    @patch('variant_explorer.ensembl_api.requests.Session')
    @patch('variant_explorer.ensembl_api.time')
    def test_make_request_rate_limit(self, mock_time, mock_session):
        """Test rate limiting in _make_request."""
        # Set up mocks
        mock_time.time.side_effect = [100.0, 100.05]  # First call, second call
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Initialize API with rate_limit = 0.1
        api = EnsemblAPI(rate_limit=0.1)
        api.last_request_time = 100.0  # Set last request time
        
        # Call the method
        api._make_request("test_endpoint")
        
        # Check that time.sleep was called with the correct value
        # (0.1 - 0.05) = 0.05 seconds
        mock_time.sleep.assert_called_once_with(0.05)
    
    @patch('variant_explorer.ensembl_api.requests.Session')
    def test_make_request_error(self, mock_session):
        """Test error handling in _make_request."""
        # Set up mock to raise an exception
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Call the method and check that it raises the exception
        with pytest.raises(Exception, match="API Error"):
            self.api._make_request("test_endpoint") 