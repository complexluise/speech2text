

import pytest
from unittest.mock import MagicMock, patch
from speech2text import llm_service

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    # Create a mock for the model instance
    mock_model = MagicMock()
    
    # Create a mock for the response object, which has a .text attribute
    mock_response = MagicMock()
    mock_model.generate_content.return_value = mock_response

    # Use patch to replace the class with a factory that returns our mock instance
    with patch('google.generativeai.GenerativeModel', return_value=mock_model) as mock_class:
        yield mock_model, mock_response

@patch('speech2text.llm_service.GEMINI_API_KEY', 'fake-api-key')
def test_correct_text_chunk_success(mock_generative_model):
    """Test that correct_text_chunk returns the corrected text on success."""
    mock_model, mock_response = mock_generative_model
    mock_response.text = "This is the corrected text."
    
    result = llm_service.correct_text_chunk("this is the incorect text")
    
    mock_model.generate_content.assert_called_once()
    assert result == "This is the corrected text."

@patch('speech2text.llm_service.GEMINI_API_KEY', 'fake-api-key')
def test_correct_text_chunk_api_error(mock_generative_model):
    """Test that correct_text_chunk returns an empty string if the API call fails."""
    mock_model, _ = mock_generative_model
    mock_model.generate_content.side_effect = Exception("API Error")
    
    result = llm_service.correct_text_chunk("some text")
    
    assert result == ""

@patch('speech2text.llm_service.GEMINI_API_KEY', None)
def test_get_model_no_api_key():
    """Test that get_model returns None if the API key is not set."""
    assert llm_service.get_model() is None

@patch('speech2text.llm_service.GEMINI_API_KEY', 'fake-api-key')
def test_structure_initial_chunk_success(mock_generative_model):
    """Test successful structuring of the first chunk."""
    mock_model, mock_response = mock_generative_model
    mock_response.text = "## Initial Title\n\nStructured content."
    
    result = llm_service.structure_initial_chunk("raw content")
    
    mock_model.generate_content.assert_called_once()
    assert result == "## Initial Title\n\nStructured content."

@patch('speech2text.llm_service.GEMINI_API_KEY', 'fake-api-key')
def test_structure_and_join_chunk_success(mock_generative_model):
    """Test successful structuring and joining of a subsequent chunk."""
    mock_model, mock_response = mock_generative_model
    mock_response.text = "## New Section\n\nMore content."
    
    result = llm_service.structure_and_join_chunk("previous context", "new chunk")
    
    mock_model.generate_content.assert_called_once()
    assert "previous context" in mock_model.generate_content.call_args[0][0]
    assert "new chunk" in mock_model.generate_content.call_args[0][0]
    assert result == "## New Section\n\nMore content."

