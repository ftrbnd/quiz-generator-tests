import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
import tempfile


# Sample test data
SAMPLE_POOLS = {
    "Topic 1: NLP": [
        "What does NLP stand for?",
        "What is tokenization?",
        "Name one NLP application."
    ],
    "Topic 2: Machine Learning": [
        "What is supervised learning?",
        "Define overfitting.",
        "What is a dataset?"
    ],
    "Topic 3: Deep Learning": [
        "What is a neural network?",
        "Define activation function.",
        "What is backpropagation?"
    ]
}

SAMPLE_SETTINGS = {
    "Topic 1: NLP": 1,
    "Topic 2: Machine Learning": 1,
    "Topic 3: Deep Learning": 1
}


class TestGenerateQuizFromPools:
    """Test suite for generate_quiz_from_pools function"""
    
    def test_basic_quiz_generation(self):
        """Test basic quiz generation with standard settings"""
        from terminal.question_pools import generate_quiz_from_pools
        
        # Set random seed for reproducibility
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, SAMPLE_SETTINGS)
        
        assert isinstance(result, list)
        assert len(result) == 3  # 1 question from each topic
        
        # Each question should be a string
        for question in result:
            assert isinstance(question, str)
    
    def test_multiple_questions_per_topic(self):
        """Test selecting multiple questions from each pool"""
        from terminal.question_pools import generate_quiz_from_pools
        
        import random
        random.seed(42)
        
        settings = {
            "Topic 1: NLP": 2,
            "Topic 2: Machine Learning": 2,
            "Topic 3: Deep Learning": 2
        }
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        assert len(result) == 6  # 2 questions from each of 3 topics
    
    def test_all_questions_from_pool(self):
        """Test selecting all questions from a pool"""
        from terminal.question_pools import generate_quiz_from_pools
        
        import random
        random.seed(42)
        
        settings = {
            "Topic 1: NLP": 3,  # All 3 questions
            "Topic 2: Machine Learning": 3,
            "Topic 3: Deep Learning": 3
        }
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        assert len(result) == 9  # All questions from all pools
    
    def test_zero_questions_from_topic(self):
        """Test with zero questions requested from a topic"""
        from terminal.question_pools import generate_quiz_from_pools
        
        settings = {
            "Topic 1: NLP": 0,
            "Topic 2: Machine Learning": 1,
            "Topic 3: Deep Learning": 1
        }
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        assert len(result) == 2  # Only 2 topics have questions
    
    def test_empty_settings(self):
        """Test with empty settings dictionary"""
        from terminal.question_pools import generate_quiz_from_pools
        
        settings = {}
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        # Should return empty list since no topics are requested
        assert len(result) == 0
    
    def test_missing_topic_in_settings(self):
        """Test when a topic exists in pools but not in settings"""
        from terminal.question_pools import generate_quiz_from_pools
        
        settings = {
            "Topic 1: NLP": 1,
            # Topic 2 and 3 are missing - should default to 0
        }
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        assert len(result) == 1  # Only 1 topic has settings
    
    def test_single_topic_pool(self):
        """Test with only one topic"""
        from terminal.question_pools import generate_quiz_from_pools
        
        pools = {
            "Topic 1: NLP": ["Q1", "Q2", "Q3"]
        }
        settings = {
            "Topic 1: NLP": 2
        }
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 2
    
    def test_randomness(self):
        """Test that questions are randomly selected"""
        from terminal.question_pools import generate_quiz_from_pools
        
        import random
        
        # Generate multiple quizzes and check they're different
        results = []
        for seed in range(5):
            random.seed(seed)
            quiz = generate_quiz_from_pools(SAMPLE_POOLS, SAMPLE_SETTINGS)
            results.append(quiz)
        
        # At least some quizzes should be different
        unique_quizzes = [tuple(r) for r in results]
        assert len(set(unique_quizzes)) > 1
    
    def test_questions_come_from_correct_pools(self):
        """Test that selected questions actually exist in their pools"""
        from terminal.question_pools import generate_quiz_from_pools
        
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, SAMPLE_SETTINGS)
        
        # Flatten all questions from all pools
        all_questions = []
        for questions in SAMPLE_POOLS.values():
            all_questions.extend(questions)
        
        # Each result question should be in the original pools
        for question in result:
            assert question in all_questions
    
    def test_no_duplicate_questions(self):
        """Test that no duplicate questions are selected from same pool"""
        from terminal.question_pools import generate_quiz_from_pools
        
        import random
        random.seed(42)
        
        settings = {
            "Topic 1: NLP": 3,  # All questions from this pool
        }
        
        result = generate_quiz_from_pools(SAMPLE_POOLS, settings)
        
        # Should have no duplicates
        assert len(result) == len(set(result))
    
    def test_invalid_amount_exceeds_pool_size(self):
        """Test behavior when requesting more questions than available"""
        from terminal.question_pools import generate_quiz_from_pools
        
        settings = {
            "Topic 1: NLP": 10,  # More than 3 available
        }
        
        # Should raise ValueError (random.sample behavior)
        with pytest.raises(ValueError):
            generate_quiz_from_pools(SAMPLE_POOLS, settings)
    
    def test_empty_pool(self):
        """Test with an empty question pool"""
        from terminal.question_pools import generate_quiz_from_pools
        
        pools = {
            "Empty Topic": [],
            "Topic 1: NLP": ["Q1", "Q2"]
        }
        settings = {
            "Empty Topic": 0,
            "Topic 1: NLP": 1
        }
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 1


class TestSaveTemplate:
    """Test suite for save_template function"""
    
    def test_save_template_default_filename(self):
        """Test saving template with default filename"""
        from terminal.question_pools import save_template
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "quiz_template.json")
            
            # Mock to capture print output
            with patch('builtins.print') as mock_print:
                with patch('builtins.open', mock_open()) as mock_file:
                    # Override the open to write to temp directory
                    save_template(SAMPLE_SETTINGS, filename=filepath)
                    
                    # Verify file was opened for writing
                    mock_file.assert_called_once()
    
    def test_save_template_custom_filename(self):
        """Test saving template with custom filename"""
        from terminal.question_pools import save_template
        
        custom_filename = "custom_template.json"
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('builtins.print'):
                save_template(SAMPLE_SETTINGS, filename=custom_filename)
                
                # Verify custom filename was used
                mock_file.assert_called_with(custom_filename, "w")
    
    def test_save_template_content(self):
        """Test that template content is correctly formatted JSON"""
        from terminal.question_pools import save_template
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('builtins.print'):
                save_template(SAMPLE_SETTINGS, filename=tmp_path)
            
            # Read back and verify JSON structure
            with open(tmp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == SAMPLE_SETTINGS
            assert "Topic 1: NLP" in loaded
            assert loaded["Topic 1: NLP"] == 1
        finally:
            os.unlink(tmp_path)
    
    def test_save_template_indent(self):
        """Test that saved JSON is properly indented"""
        from terminal.question_pools import save_template
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('builtins.print'):
                save_template(SAMPLE_SETTINGS, filename=tmp_path)
            
            # Read as text to check formatting
            with open(tmp_path, 'r') as f:
                content = f.read()
            
            # Should contain newlines (indented JSON)
            assert '\n' in content
            # Should contain proper indentation
            assert '    ' in content
        finally:
            os.unlink(tmp_path)
    
    def test_save_template_empty_settings(self):
        """Test saving empty settings"""
        from terminal.question_pools import save_template
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('builtins.print'):
                save_template({}, filename=tmp_path)
            
            with open(tmp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == {}
        finally:
            os.unlink(tmp_path)
    
    def test_save_template_print_message(self):
        """Test that save_template prints confirmation message"""
        from terminal.question_pools import save_template
        
        filename = "test_template.json"
        
        with patch('builtins.open', mock_open()):
            with patch('builtins.print') as mock_print:
                save_template(SAMPLE_SETTINGS, filename=filename)
                
                # Verify print was called with correct message
                mock_print.assert_called_once_with(f"Template saved as {filename}")


class TestRunQuestionPools:
    """Test suite for run_question_pools function"""
    
    @patch('builtins.print')
    @patch('terminal.question_pools.save_template')
    @patch('terminal.question_pools.generate_quiz_from_pools')
    def test_run_question_pools_execution(self, mock_generate, mock_save, mock_print):
        """Test that run_question_pools executes all steps"""
        from terminal.question_pools import run_question_pools
        
        # Mock the quiz generation to return a predictable result
        mock_generate.return_value = ["Q1", "Q2", "Q3"]
        
        run_question_pools()
        
        # Verify generate_quiz_from_pools was called
        mock_generate.assert_called_once()
        
        # Verify save_template was called
        mock_save.assert_called_once()
        
        # Verify print statements were made
        assert mock_print.call_count > 0
    
    @patch('builtins.print')
    @patch('terminal.question_pools.save_template')
    @patch('terminal.question_pools.generate_quiz_from_pools')
    def test_run_question_pools_output_format(self, mock_generate, mock_save, mock_print):
        """Test that output is properly formatted"""
        from terminal.question_pools import run_question_pools
        
        mock_quiz = ["Q1", "Q2", "Q3"]
        mock_generate.return_value = mock_quiz
        
        run_question_pools()
        
        # Check that questions are printed with numbering
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Should contain header message
        assert any("Generating quiz" in str(call) for call in print_calls)
        
        # Should contain question numbering
        assert any("1." in str(call) for call in print_calls)


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_unicode_questions(self):
        """Test with unicode characters in questions"""
        from terminal.question_pools import generate_quiz_from_pools
        
        pools = {
            "Unicode Topic": [
                "¿Qué es NLP?",
                "Was ist künstliche Intelligenz?",
                "什么是机器学习？"
            ]
        }
        settings = {"Unicode Topic": 2}
        
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 2
        for question in result:
            assert isinstance(question, str)
    
    def test_very_long_questions(self):
        """Test with very long question strings"""
        from terminal.question_pools import generate_quiz_from_pools
        
        long_question = "This is a very long question " * 50
        pools = {
            "Long Topic": [long_question, "Short question"]
        }
        settings = {"Long Topic": 1}
        
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 1
        assert isinstance(result[0], str)
    
    def test_special_characters_in_topic_names(self):
        """Test with special characters in topic names"""
        from terminal.question_pools import generate_quiz_from_pools
        
        pools = {
            "Topic #1: AI/ML": ["Q1", "Q2"],
            "Topic @2: NLP & DL": ["Q3", "Q4"]
        }
        settings = {
            "Topic #1: AI/ML": 1,
            "Topic @2: NLP & DL": 1
        }
        
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 2
    
    def test_numeric_question_content(self):
        """Test questions containing only numbers"""
        from terminal.question_pools import generate_quiz_from_pools
        
        pools = {
            "Math": ["2 + 2 = ?", "10 * 5 = ?", "100 / 4 = ?"]
        }
        settings = {"Math": 2}
        
        import random
        random.seed(42)
        
        result = generate_quiz_from_pools(pools, settings)
        
        assert len(result) == 2


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_full_workflow(self):
        """Test complete workflow from generation to saving"""
        from terminal.question_pools import generate_quiz_from_pools, save_template
        
        import random
        random.seed(42)
        
        # Generate quiz
        quiz = generate_quiz_from_pools(SAMPLE_POOLS, SAMPLE_SETTINGS)
        
        assert len(quiz) > 0
        
        # Save template
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('builtins.print'):
                save_template(SAMPLE_SETTINGS, filename=tmp_path)
            
            # Verify file exists and is valid JSON
            assert os.path.exists(tmp_path)
            
            with open(tmp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == SAMPLE_SETTINGS
        finally:
            os.unlink(tmp_path)
    
    def test_load_and_regenerate_quiz(self):
        """Test saving template and using it to regenerate quiz"""
        from terminal.question_pools import generate_quiz_from_pools, save_template
        
        import random
        
        # Generate and save
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            random.seed(42)
            quiz1 = generate_quiz_from_pools(SAMPLE_POOLS, SAMPLE_SETTINGS)
            
            with patch('builtins.print'):
                save_template(SAMPLE_SETTINGS, filename=tmp_path)
            
            # Load template
            with open(tmp_path, 'r') as f:
                loaded_settings = json.load(f)
            
            # Regenerate with loaded settings
            random.seed(42)
            quiz2 = generate_quiz_from_pools(SAMPLE_POOLS, loaded_settings)
            
            # Should produce same quiz with same seed
            assert quiz1 == quiz2
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])