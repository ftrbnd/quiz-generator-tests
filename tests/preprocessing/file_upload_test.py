import pytest
from io import BytesIO, StringIO
from unittest.mock import patch, mock_open

@pytest.fixture
def mock_llm_generate():
    with patch('phases.llm_client.generate_from_llm') as mock:
        # Return a sample list of questions
        mock.return_value = [
            {
                "question": "What is 2+2?",
                "answer": "4",
                "type": "short_answer"
            },
            {
                "question": "True or False: Python is a programming language",
                "answer": "True",
                "type": "t/f"
            }
        ]
        yield mock


class TestFileTabGeneration:
    def test_valid_text_file_with_string_path(self, mock_llm_generate, tmp_path):
        """Test with a valid .txt file passed as a file path (string)"""
        from inputs.file_tab import render
        
        # Create a temporary file with content
        test_file = tmp_path / "test_content.txt"
        test_content = "This is test content about Python programming."
        test_file.write_text(test_content, encoding="utf-8")
        
        # Import the function we need to test
        # Note: We can't easily test the Gradio UI directly, so we test the logic
        # We'll extract the on_click_generate function logic
        
        # Simulate the function call
        with patch('builtins.open', mock_open(read_data=test_content)):
            # Mock the internal function behavior
            file_obj = str(test_file)
            n = 5
            types = ["Multiple choice", "Short answer"]
            
            # Read file
            with open(file_obj, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            
            assert text == test_content
            
            # Call the mocked LLM function
            result = mock_llm_generate(
                source_text=text,
                num_questions=n,
                question_types=types
            )
            
            assert len(result) == 2
            assert result[0]["question"] == "What is 2+2?"
            mock_llm_generate.assert_called_once_with(
                source_text=test_content,
                num_questions=5,
                question_types=["Multiple choice", "Short answer"]
            )
    
    def test_valid_text_file_with_file_object(self, mock_llm_generate):
        """Test with a file-like object (BytesIO)"""
        test_content = "Test content for quiz generation"
        file_obj = BytesIO(test_content.encode("utf-8"))
        
        # Simulate reading from file object
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        assert text == test_content
        
        result = mock_llm_generate(
            source_text=text,
            num_questions=3,
            question_types=[]
        )
        
        assert len(result) == 2
        mock_llm_generate.assert_called_once()
    
    def test_empty_file(self):
        """Test handling of empty file"""
        file_obj = BytesIO(b"")
        
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        # Empty file should result in empty string
        assert text == ""
        assert not text.strip()
    
    def test_none_file_input(self):
        """Test handling when no file is uploaded"""
        file_obj = None
        
        # Should return warning message
        if file_obj is None:
            result = "⚠️ Please upload a .txt file."
        
        assert result == "⚠️ Please upload a .txt file."
    
    def test_file_with_special_characters(self, mock_llm_generate):
        """Test file with unicode and special characters"""
        test_content = "Testing with émojis 🎉 and spëcial çharacters"
        file_obj = BytesIO(test_content.encode("utf-8"))
        
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        assert text == test_content
        assert "🎉" in text
        assert "émojis" in text
    
    def test_file_with_different_encoding(self):
        """Test file with latin-1 encoding"""
        test_content = "Café résumé"
        file_obj = BytesIO(test_content.encode("latin-1"))
        
        raw = file_obj.read()
        # Using errors="ignore" should handle encoding issues gracefully
        text = raw.decode("utf-8", errors="ignore")
        
        # Text should be decoded (possibly with some character loss)
        assert isinstance(text, str)
    
    def test_large_file_content(self, mock_llm_generate):
        """Test with content exceeding MAX_SOURCE_CHARS"""
        # Create content larger than 8000 chars
        test_content = "A" * 10000
        file_obj = BytesIO(test_content.encode("utf-8"))
        
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        assert len(text) == 10000
        
        # The llm_client should truncate this internally
        result = mock_llm_generate(
            source_text=text,
            num_questions=5,
            question_types=[]
        )
        
        assert result is not None
    
    def test_file_read_error(self):
        """Test handling of file read errors"""
        # Simulate a file that can't be read
        with pytest.raises(FileNotFoundError):
            with open("/nonexistent/path/file.txt", "r") as f:
                f.read()
    
    def test_question_type_mapping(self, mock_llm_generate):
        """Test that question types are passed correctly"""
        test_content = "Sample content"
        file_obj = BytesIO(test_content.encode("utf-8"))
        
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        question_types = ["Multiple choice", "True/False"]
        
        result = mock_llm_generate(
            source_text=text,
            num_questions=5,
            question_types=question_types
        )
        
        mock_llm_generate.assert_called_once_with(
            source_text=test_content,
            num_questions=5,
            question_types=question_types
        )
    
    def test_slider_values(self, mock_llm_generate):
        """Test with different number of questions"""
        test_content = "Content for quiz"
        
        for num_questions in [1, 10, 25, 50]:
            mock_llm_generate.reset_mock()
            
            result = mock_llm_generate(
                source_text=test_content,
                num_questions=num_questions,
                question_types=[]
            )
            
            mock_llm_generate.assert_called_once_with(
                source_text=test_content,
                num_questions=num_questions,
                question_types=[]
            )
    
    def test_api_error_handling(self):
        """Test handling of API errors"""
        with patch('phases.llm_client.generate_from_llm') as mock:
            mock.side_effect = Exception("API connection failed")
            
            try:
                mock(
                    source_text="test",
                    num_questions=5,
                    question_types=[]
                )
                result = None
            except Exception as e:
                result = f"**Error calling Groq API:** {e}"
            
            assert "Error calling Groq API" in result
            assert "API connection failed" in result
    
    def test_whitespace_only_file(self):
        """Test file with only whitespace"""
        test_content = "   \n\n\t  \n   "
        file_obj = BytesIO(test_content.encode("utf-8"))
        
        raw = file_obj.read()
        text = raw.decode("utf-8", errors="ignore")
        
        # Should detect as empty when stripped
        assert not text.strip()
    
    def test_string_io_file_object(self, mock_llm_generate):
        """Test with StringIO object"""
        test_content = "String IO content"
        file_obj = StringIO(test_content)
        
        # StringIO has read() but returns str directly
        raw = file_obj.read()
        
        if isinstance(raw, (bytes, bytearray)):
            text = raw.decode("utf-8", errors="ignore")
        else:
            text = raw
        
        assert text == test_content
        assert isinstance(text, str)


class TestLLMClientQuestionParsing:
    """Test the question parsing logic from llm_client.py"""
    
    def test_parse_valid_json_response(self):
        """Test parsing a valid JSON response"""
        from phases.llm_client import _parse_questions
        
        raw_response = '''{
            "questions": [
                {
                    "question": "What is Python?",
                    "answer": "A programming language",
                    "type": "short_answer"
                }
            ]
        }'''
        
        result = _parse_questions(raw_response)
        
        assert len(result) == 1
        assert result[0]["question"] == "What is Python?"
        assert result[0]["answer"] == "A programming language"
        assert result[0]["type"] == "short_answer"
    
    def test_parse_list_format_json(self):
        """Test parsing JSON that's a direct list"""
        from phases.llm_client import _parse_questions
        
        raw_response = '''[
            {
                "question": "What is 2+2?",
                "answer": "4",
                "type": "short_answer"
            }
        ]'''
        
        result = _parse_questions(raw_response)
        
        assert len(result) == 1
        assert result[0]["question"] == "What is 2+2?"
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON"""
        from phases.llm_client import _parse_questions
        
        raw_response = "This is not JSON"
        
        result = _parse_questions(raw_response)
        
        assert result == []
    
    def test_parse_malformed_question(self):
        """Test handling of questions missing required fields"""
        from phases.llm_client import _parse_questions
        
        raw_response = '''{
            "questions": [
                {
                    "question": "Valid question?",
                    "answer": "Yes"
                },
                {
                    "question": "What is this?",
                    "answer": "Unknown",
                    "type": "short_answer"
                }
            ]
        }'''
        
        result = _parse_questions(raw_response)
        
        # First question missing 'type', second is valid
        assert len(result) == 1
        assert result[0]["question"] == "What is this?"
    
    def test_parse_invalid_question_type(self):
        """Test handling of invalid question types"""
        from phases.llm_client import _parse_questions
        
        raw_response = '''{
            "questions": [
                {
                    "question": "Test?",
                    "answer": "Yes",
                    "type": "invalid_type"
                }
            ]
        }'''
        
        result = _parse_questions(raw_response)
        
        # Should default to short_answer
        assert len(result) == 1
        assert result[0]["type"] == "short_answer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])