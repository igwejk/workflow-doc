"""
Test the CLI app.
"""

from pathlib import Path

from typer.testing import CliRunner

from workflowdoc import app

runner = CliRunner()


def test_app():
    """
    Test the CLI app.
    """

    result = runner.invoke(
        app,
        ["generate", str(Path(__file__).parent / "fixtures" / "test.0.yaml")],
    )

    assert result.exit_code == 0

    expected_md_file_content = (
        Path(__file__).parent / "fixtures" / "test.0.expected.md"
    ).read_text(encoding="utf-8")
    actual_md_file_content = (
        Path(__file__).parent / "fixtures" / "test.0.yaml.md"
    ).read_text(encoding="utf-8")
    assert actual_md_file_content == expected_md_file_content
