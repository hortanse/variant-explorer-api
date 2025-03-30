"""
Tests for the main module.
"""

import io
import sys
import pytest
from unittest.mock import patch, MagicMock
from variant_explorer.main import (
    setup_logging,
    process_gene_query,
    process_variant_query,
    filter_fields,
    write_output,
    main
)


class TestMain:
    """Test cases for the main module."""
    
    @patch('variant_explorer.main.logging')
    def test_setup_logging_verbose(self, mock_logging):
        """Test logging setup with verbose mode enabled."""
        setup_logging(verbose=True)
        mock_logging.DEBUG.assert_called_once()
        mock_logging.basicConfig.assert_called_once()
    
    @patch('variant_explorer.main.logging')
    def test_setup_logging_non_verbose(self, mock_logging):
        """Test logging setup with verbose mode disabled."""
        setup_logging(verbose=False)
        mock_logging.INFO.assert_called_once()
        mock_logging.basicConfig.assert_called_once()
    
    @patch('variant_explorer.main.OutputFormatter')
    def test_process_gene_query(self, mock_formatter):
        """Test processing a gene query."""
        # Set up mocks
        mock_api = MagicMock()
        mock_api.get_gene_info.return_value = {"id": "ENSG00000012048", "display_name": "BRCA1"}
        mock_api.get_gene_function.return_value = [{"dbname": "GO", "description": "DNA repair"}]
        mock_api.get_gene_pathways.return_value = [{"dbname": "Reactome", "description": "HR repair"}]
        
        mock_formatter.format_gene_data.return_value = {
            "gene_symbol": "BRCA1",
            "function": "DNA repair",
            "pathways": "HR repair"
        }
        
        # Call the method
        results = process_gene_query(mock_api, ["BRCA1"], verbose=True)
        
        # Check the results
        assert len(results) == 1
        assert results[0]["gene_symbol"] == "BRCA1"
        
        # Check that the API methods were called
        mock_api.get_gene_info.assert_called_once_with("BRCA1", "human")
        mock_api.get_gene_function.assert_called_once()
        mock_api.get_gene_pathways.assert_called_once()
        mock_formatter.format_gene_data.assert_called_once()
    
    @patch('variant_explorer.main.OutputFormatter')
    def test_process_gene_query_with_phenotypes(self, mock_formatter):
        """Test processing a gene query with phenotypes."""
        # Set up mocks
        mock_api = MagicMock()
        mock_api.get_gene_info.return_value = {"id": "ENSG00000012048", "display_name": "BRCA1"}
        mock_api.get_gene_phenotypes.return_value = [{"phenotype": {"description": "Cancer"}}]
        
        # Call the method
        process_gene_query(mock_api, ["BRCA1"], include_phenotypes=True, verbose=True)
        
        # Check that the API methods were called
        mock_api.get_gene_phenotypes.assert_called_once()
        mock_formatter.format_gene_data.assert_called_once()
    
    @patch('variant_explorer.main.logging')
    @patch('variant_explorer.main.OutputFormatter')
    def test_process_gene_query_error(self, mock_formatter, mock_logging):
        """Test error handling in gene query processing."""
        # Set up mocks
        mock_api = MagicMock()
        mock_api.get_gene_info.side_effect = Exception("API Error")
        
        # Call the method
        results = process_gene_query(mock_api, ["BRCA1"], verbose=True)
        
        # Check results
        assert len(results) == 0
        mock_logging.error.assert_called_once()
    
    @patch('variant_explorer.main.OutputFormatter')
    def test_process_variant_query(self, mock_formatter):
        """Test processing a variant query."""
        # Set up mocks
        mock_api = MagicMock()
        mock_api.get_variant_info.return_value = [
            {"id": "rs80357906", "most_severe_consequence": "missense_variant"}
        ]
        
        mock_formatter.format_variant_data.return_value = {
            "variant_id": "rs80357906",
            "variant_effect": "missense_variant"
        }
        
        # Call the method
        results = process_variant_query(mock_api, ["chr17:41245466:G:A"], verbose=True)
        
        # Check the results
        assert len(results) == 1
        assert results[0]["variant_id"] == "rs80357906"
        
        # Check that the API methods were called
        mock_api.get_variant_info.assert_called_once_with("chr17:41245466:G:A", "GRCh38")
        mock_formatter.format_variant_data.assert_called_once()
    
    @patch('variant_explorer.main.logging')
    @patch('variant_explorer.main.OutputFormatter')
    def test_process_variant_query_error(self, mock_formatter, mock_logging):
        """Test error handling in variant query processing."""
        # Set up mocks
        mock_api = MagicMock()
        mock_api.get_variant_info.side_effect = Exception("API Error")
        
        # Call the method
        results = process_variant_query(mock_api, ["chr17:41245466:G:A"], verbose=True)
        
        # Check results
        assert len(results) == 0
        mock_logging.error.assert_called_once()
    
    def test_filter_fields(self):
        """Test filtering fields from data."""
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
        result = filter_fields(data, "gene_symbol,gene_id")
        
        # Check results
        assert len(result) == 2
        assert list(result[0].keys()) == ["gene_symbol", "gene_id"]
        assert "description" not in result[0]
        assert "function" not in result[0]
    
    def test_filter_fields_no_filter(self):
        """Test filter_fields when no filter is provided."""
        # Input data
        data = [{"gene_symbol": "BRCA1", "gene_id": "ENSG00000012048"}]
        
        # Call the method
        result = filter_fields(data, None)
        
        # Check results
        assert result == data
    
    @patch('variant_explorer.main.OutputFormatter')
    @patch('variant_explorer.main.print')
    def test_write_output_stdout_csv(self, mock_print, mock_formatter):
        """Test writing output to stdout in CSV format."""
        # Input data
        data = [{"gene_symbol": "BRCA1", "gene_id": "ENSG00000012048"}]
        
        # Call the method
        write_output(data, output_file=None, output_format="csv")
        
        # Check that the formatter was called
        mock_formatter.to_csv.assert_called_once_with(data, sys.stdout)
    
    @patch('variant_explorer.main.OutputFormatter')
    @patch('variant_explorer.main.print')
    def test_write_output_stdout_json(self, mock_print, mock_formatter):
        """Test writing output to stdout in JSON format."""
        # Input data
        data = [{"gene_symbol": "BRCA1", "gene_id": "ENSG00000012048"}]
        
        # Call the method
        write_output(data, output_file=None, output_format="json")
        
        # Check that the formatter was called
        mock_formatter.to_json.assert_called_once_with(data, sys.stdout)
    
    @patch('variant_explorer.main.open')
    @patch('variant_explorer.main.OutputFormatter')
    @patch('variant_explorer.main.print')
    def test_write_output_file_csv(self, mock_print, mock_formatter, mock_open):
        """Test writing output to a file in CSV format."""
        # Input data
        data = [{"gene_symbol": "BRCA1", "gene_id": "ENSG00000012048"}]
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Call the method
        write_output(data, output_file="output.csv", output_format="csv")
        
        # Check that the formatter and open were called
        mock_open.assert_called_once_with("output.csv", "w")
        mock_formatter.to_csv.assert_called_once_with(data, mock_file)
        mock_print.assert_called_once()
    
    @patch('variant_explorer.main.print')
    def test_write_output_no_data(self, mock_print):
        """Test writing output when there's no data."""
        # Call the method
        write_output([], output_file=None, output_format="csv")
        
        # Check that print was called with an error message
        mock_print.assert_called_once()
        args, kwargs = mock_print.call_args
        assert "No results found" in args[0]
        assert kwargs["file"] == sys.stderr
    
    @patch('variant_explorer.main.parse_args')
    @patch('variant_explorer.main.setup_logging')
    @patch('variant_explorer.main.EnsemblAPI')
    @patch('variant_explorer.main.process_gene_query')
    @patch('variant_explorer.main.write_output')
    def test_main_gene_command(self, mock_write_output, mock_process_gene, mock_ensembl_api, 
                               mock_setup_logging, mock_parse_args):
        """Test main function with gene command."""
        # Set up mocks
        args = MagicMock()
        args.command = "gene"
        args.symbols = ["BRCA1"]
        args.species = "human"
        args.include_transcripts = False
        args.include_phenotypes = False
        args.verbose = False
        args.fields = None
        args.output = None
        args.format = "csv"
        mock_parse_args.return_value = args
        
        mock_api_instance = MagicMock()
        mock_ensembl_api.return_value = mock_api_instance
        
        mock_process_gene.return_value = [{"gene_symbol": "BRCA1"}]
        
        # Call the function
        result = main()
        
        # Check the result
        assert result == 0
        
        # Check that the methods were called
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with(False)
        mock_ensembl_api.assert_called_once()
        mock_process_gene.assert_called_once_with(
            api=mock_api_instance,
            symbols=["BRCA1"],
            species="human",
            include_transcripts=False,
            include_phenotypes=False,
            verbose=False
        )
        mock_write_output.assert_called_once_with(
            data=[{"gene_symbol": "BRCA1"}],
            output_file=None,
            output_format="csv"
        )
    
    @patch('variant_explorer.main.parse_args')
    @patch('variant_explorer.main.setup_logging')
    @patch('variant_explorer.main.EnsemblAPI')
    @patch('variant_explorer.main.process_variant_query')
    @patch('variant_explorer.main.write_output')
    def test_main_variant_command(self, mock_write_output, mock_process_variant, mock_ensembl_api,
                                 mock_setup_logging, mock_parse_args):
        """Test main function with variant command."""
        # Set up mocks
        args = MagicMock()
        args.command = "variant"
        args.variants = ["chr17:41245466:G:A"]
        args.assembly = "GRCh38"
        args.include_populations = False
        args.verbose = False
        args.fields = None
        args.output = None
        args.format = "csv"
        mock_parse_args.return_value = args
        
        mock_api_instance = MagicMock()
        mock_ensembl_api.return_value = mock_api_instance
        
        mock_process_variant.return_value = [{"variant_id": "rs80357906"}]
        
        # Call the function
        result = main()
        
        # Check the result
        assert result == 0
        
        # Check that the methods were called
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once_with(False)
        mock_ensembl_api.assert_called_once()
        mock_process_variant.assert_called_once_with(
            api=mock_api_instance,
            variants=["chr17:41245466:G:A"],
            assembly="GRCh38",
            include_populations=False,
            verbose=False
        )
        mock_write_output.assert_called_once_with(
            data=[{"variant_id": "rs80357906"}],
            output_file=None,
            output_format="csv"
        )
    
    @patch('variant_explorer.main.parse_args')
    @patch('variant_explorer.main.setup_logging')
    @patch('variant_explorer.main.logging')
    def test_main_unknown_command(self, mock_logging, mock_setup_logging, mock_parse_args):
        """Test main function with unknown command."""
        # Set up mocks
        args = MagicMock()
        args.command = "unknown"
        mock_parse_args.return_value = args
        
        # Call the function
        result = main()
        
        # Check the result
        assert result == 1
        mock_logging.error.assert_called_once()
    
    @patch('variant_explorer.main.parse_args')
    @patch('variant_explorer.main.setup_logging')
    @patch('variant_explorer.main.logging')
    def test_main_exception(self, mock_logging, mock_setup_logging, mock_parse_args):
        """Test main function when an exception occurs."""
        # Set up mocks
        mock_parse_args.side_effect = Exception("Test Error")
        
        # Call the function
        result = main()
        
        # Check the result
        assert result == 1
        mock_logging.error.assert_called_once() 