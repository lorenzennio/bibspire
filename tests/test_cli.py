"""
Unit tests for BibSpire CLI
"""

from unittest.mock import Mock, patch

import pytest

from bibspire.cli import main


class TestCLI:
    """Test CLI functionality"""

    @patch("bibspire.cli.BibSpire")
    @patch("sys.argv", ["bibspire", "test.bib"])
    def test_basic_usage(self, mock_bibspire_class):
        """Test basic CLI usage"""
        mock_bibspire = Mock()
        mock_bibspire_class.return_value = mock_bibspire

        main()

        mock_bibspire_class.assert_called_once_with(delay=1.0, verbose=False)
        mock_bibspire.update_bib_file.assert_called_once_with("test.bib", None)

    @patch("bibspire.cli.BibSpire")
    @patch("sys.argv", ["bibspire", "input.bib", "-o", "output.bib", "-v", "-d", "2.0"])
    def test_full_options(self, mock_bibspire_class):
        """Test CLI with all options"""
        mock_bibspire = Mock()
        mock_bibspire_class.return_value = mock_bibspire

        main()

        mock_bibspire_class.assert_called_once_with(delay=2.0, verbose=True)
        mock_bibspire.update_bib_file.assert_called_once_with("input.bib", "output.bib")

    @patch("sys.argv", ["bibspire", "--version"])
    def test_version(self, capsys):
        """Test version output"""
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "1.0.0" in captured.out

    @patch("sys.argv", ["bibspire", "--help"])
    def test_help(self, capsys):
        """Test help output"""
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Update .bib file entries" in captured.out
        assert "input_file" in captured.out

    @patch("bibspire.cli.BibSpire")
    @patch("sys.argv", ["bibspire", "test.bib"])
    def test_keyboard_interrupt(self, mock_bibspire_class, capsys):
        """Test handling of keyboard interrupt"""
        mock_bibspire = Mock()
        mock_bibspire_class.return_value = mock_bibspire
        mock_bibspire.update_bib_file.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Interrupted by user" in captured.out

    @patch("bibspire.cli.BibSpire")
    @patch("sys.argv", ["bibspire", "nonexistent.bib"])
    def test_file_not_found(self, mock_bibspire_class, capsys):
        """Test handling of file not found error"""
        mock_bibspire = Mock()
        mock_bibspire_class.return_value = mock_bibspire
        mock_bibspire.update_bib_file.side_effect = FileNotFoundError("File not found")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    @patch("bibspire.cli.BibSpire")
    @patch("sys.argv", ["bibspire", "test.bib"])
    def test_general_error(self, mock_bibspire_class, capsys):
        """Test handling of general errors"""
        mock_bibspire = Mock()
        mock_bibspire_class.return_value = mock_bibspire
        mock_bibspire.update_bib_file.side_effect = Exception("Some error")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Some error" in captured.out
