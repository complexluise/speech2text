

import json
import pytest
from click.testing import CliRunner
from speech2text.cli import cli

@pytest.fixture
def mock_llm_service(mocker):
    """Fixture to mock all functions in the llm_service module."""
    mocker.patch('speech2text.cli.llm_service.correct_text_chunk', side_effect=lambda x: f"corrected: {x}")
    mocker.patch('speech2text.cli.llm_service.structure_initial_chunk', side_effect=lambda x: f"## Initial\n{x}")
    mocker.patch('speech2text.cli.llm_service.structure_and_join_chunk', side_effect=lambda ctx, new: f"## New Section\n{new}")

@pytest.fixture
def job_dir(tmp_path):
    """Creates a temporary job directory with dummy transcription files."""
    d = tmp_path / "test_job"
    d.mkdir()
    
    part_0_data = {"transcript": "this is part one."}
    with open(d / "job_part_000.json", "w") as f:
        json.dump(part_0_data, f)
        
    part_1_data = {"transcript": "this is part two."}
    with open(d / "job_part_001.json", "w") as f:
        json.dump(part_1_data, f)
        
    return str(d)

def test_post_process_success(mock_llm_service, job_dir):
    """Test the post-process command for a successful run."""
    runner = CliRunner()
    output_file = job_dir + "/result.md"
    
    result = runner.invoke(cli, ["post-process", job_dir, "--output", output_file])
    
    assert result.exit_code == 0
    assert "Final Markdown document saved to" in result.output
    
    with open(output_file, "r") as f:
        content = f.read()
        
    # Check that the content is what we expect from the mocked functions
    assert "## Initial" in content
    assert "corrected: this is part one." in content
    assert "## New Section" in content
    assert "corrected: this is part two." in content

def test_post_process_no_files(tmp_path):
    """Test that the command fails gracefully when no JSON files are found."""
    runner = CliRunner()
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    result = runner.invoke(cli, ["post-process", str(empty_dir)])
    
    assert result.exit_code == 0 # The app itself doesn't exit with an error code, it logs an error
    assert "No '_part_*.json' files found" in result.output

def test_post_process_default_output_name(mock_llm_service, job_dir):
    """Test that the default output file name is generated correctly."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ["post-process", job_dir])
    
    assert result.exit_code == 0
    # The default output should be in the parent directory of job_dir, named after job_dir
    assert "test_job.md" in result.output

