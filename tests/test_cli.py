"""
Tests for the command-line interface module.
"""

import pytest
from variant_explorer.cli import parse_args


class TestCLI:
    """Test cases for the CLI module."""
    
    def test_gene_command_basic(self):
        """Test basic gene command parsing."""
        args = parse_args(["gene", "BRCA1"])
        assert args.command == "gene"
        assert args.symbols == ["BRCA1"]
        assert args.species == "human"  # Default value
        assert not args.include_transcripts
        assert not args.include_phenotypes
        assert args.format == "csv"  # Default value
    
    def test_gene_command_multiple_symbols(self):
        """Test gene command with multiple symbols."""
        args = parse_args(["gene", "BRCA1", "TP53", "EGFR"])
        assert args.command == "gene"
        assert args.symbols == ["BRCA1", "TP53", "EGFR"]
    
    def test_gene_command_all_options(self):
        """Test gene command with all options."""
        args = parse_args([
            "gene", "BRCA1",
            "--species", "mouse",
            "--include-transcripts",
            "--include-phenotypes",
            "-o", "output.json",
            "-f", "json",
            "-v",
            "--fields", "gene_symbol,gene_id,description"
        ])
        assert args.command == "gene"
        assert args.symbols == ["BRCA1"]
        assert args.species == "mouse"
        assert args.include_transcripts
        assert args.include_phenotypes
        assert args.output == "output.json"
        assert args.format == "json"
        assert args.verbose
        assert args.fields == "gene_symbol,gene_id,description"
    
    def test_variant_command_basic(self):
        """Test basic variant command parsing."""
        args = parse_args(["variant", "chr17:41245466:G:A"])
        assert args.command == "variant"
        assert args.variants == ["chr17:41245466:G:A"]
        assert args.assembly == "GRCh38"  # Default value
        assert not args.include_populations
        assert args.format == "csv"  # Default value
    
    def test_variant_command_multiple_variants(self):
        """Test variant command with multiple variants."""
        args = parse_args([
            "variant",
            "chr17:41245466:G:A",
            "chr13:32315474:G:A"
        ])
        assert args.command == "variant"
        assert args.variants == ["chr17:41245466:G:A", "chr13:32315474:G:A"]
    
    def test_variant_command_all_options(self):
        """Test variant command with all options."""
        args = parse_args([
            "variant", "chr17:41245466:G:A",
            "--assembly", "GRCh37",
            "--include-populations",
            "-o", "output.json",
            "-f", "json",
            "-v",
            "--fields", "variant_id,location,reference,alternate"
        ])
        assert args.command == "variant"
        assert args.variants == ["chr17:41245466:G:A"]
        assert args.assembly == "GRCh37"
        assert args.include_populations
        assert args.output == "output.json"
        assert args.format == "json"
        assert args.verbose
        assert args.fields == "variant_id,location,reference,alternate"
    
    def test_missing_command(self):
        """Test that a missing command raises an error."""
        with pytest.raises(SystemExit):
            parse_args([])
    
    def test_invalid_command(self):
        """Test that an invalid command raises an error."""
        with pytest.raises(SystemExit):
            parse_args(["invalid_command"])
    
    def test_missing_symbols(self):
        """Test that missing symbols raise an error."""
        with pytest.raises(SystemExit):
            parse_args(["gene"])
    
    def test_missing_variants(self):
        """Test that missing variants raise an error."""
        with pytest.raises(SystemExit):
            parse_args(["variant"]) 