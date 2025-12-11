import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


# Mock transformers to avoid loading actual models during testing
sys.modules['transformers'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()


# Sample quiz text for testing
SAMPLE_QUIZ_TEXT = """
1. What does NLP stand for?
a) Natural Language Processing
b) New Logic Principle
c) Node Link Protocol
d) Neural Language Path

2. What is machine learning?
a) A type of hardware
b) A subset of AI
c) A programming language
d) A database system
"""

SAMPLE_SINGLE_QUESTION = """
1. What is Python?
a) A snake
b) A programming language
c) A type of food
d) A movie
"""

SAMPLE_QUESTION_WITH_ASTERISK = """
1. What does AI stand for?
a) Artificial Intelligence (*)
b) Automated Information
c) Applied Integration
d) Augmented Interaction
"""

SAMPLE_MULTILINE_QUESTION = """
1. Which of the following is true about 
   deep learning networks?
a) They require minimal data
b) They have multiple hidden layers
c) They are always faster than traditional ML
d) They don't need GPUs
"""


class TestExtractFirstQuestion:
    """Test suite for extract_first_question method"""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_single_question_basic(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test extracting a single question from quiz text"""
        # We need to import after mocking
        from phases.quiz_generator import QuizAI
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question(SAMPLE_QUIZ_TEXT)
        
        # Should contain question 1
        assert "1. What does NLP stand for?" in result
        assert "a) Natural Language Processing" in result
        assert "d) Neural Language Path" in result
        
        # Should NOT contain question 2
        assert "2. What is machine learning?" not in result
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_stops_at_option_d(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that extraction stops after option d"""
        from phases.quiz_generator import QuizAI
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question(SAMPLE_QUIZ_TEXT)
        
        lines = result.strip().split('\n')
        last_line = lines[-1].strip().lower()
        
        # Last line should be option d
        assert last_line.startswith('d)')
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_with_question_keyword(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test extraction when line starts with 'Question' keyword"""
        from phases.quiz_generator import QuizAI
        
        quiz_text = """
Question: What is AI?
a) Artificial Intelligence
b) Automated Integration
c) Applied Information
d) None of the above
"""
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question(quiz_text)
        
        assert "Question: What is AI?" in result
        assert "a) Artificial Intelligence" in result
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_empty_text(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test extraction with empty quiz text"""
        from phases.quiz_generator import QuizAI
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question("")
        
        assert result == ""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_whitespace_only(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test extraction with whitespace only"""
        from phases.quiz_generator import QuizAI
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question("   \n\n   ")
        
        # Should return empty or whitespace
        assert result.strip() == ""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_preserves_formatting(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that indentation and spacing are preserved"""
        from phases.quiz_generator import QuizAI
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question(SAMPLE_MULTILINE_QUESTION)
        
        # Should preserve the multiline question format
        assert "deep learning networks?" in result
        lines = result.split('\n')
        assert len(lines) > 1
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_extract_case_insensitive(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that extraction works with different cases for option d"""
        from phases.quiz_generator import QuizAI
        
        quiz_text = """
1. Test question?
a) Option A
b) Option B
c) Option C
D) Option D
"""
        
        quiz_ai = QuizAI()
        result = quiz_ai.extract_first_question(quiz_text)
        
        # Should stop at D) even though it's uppercase
        assert "D) Option D" in result


class TestGenerateExplanations:
    """Test suite for generate_explanations method"""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_basic(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test basic explanation generation"""
        from phases.quiz_generator import QuizAI
        
        # Mock the generator response
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "NLP stands for Natural Language Processing, which is a field of AI."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        # Should return the mocked explanation
        assert isinstance(result, str)
        assert "Natural Language Processing" in result
        
        # Verify generator was called
        mock_generator.assert_called_once()
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_calls_extract(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that generate_explanations calls extract_first_question"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Test explanation"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        # Spy on extract_first_question
        original_extract = quiz_ai.extract_first_question
        quiz_ai.extract_first_question = Mock(side_effect=original_extract)
        
        quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        # Verify extract was called with the quiz text
        quiz_ai.extract_first_question.assert_called_once_with(SAMPLE_QUIZ_TEXT)
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_prompt_format(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that the prompt is properly formatted"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Explanation text"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        quiz_ai.generate_explanations(SAMPLE_SINGLE_QUESTION)
        
        # Get the call arguments
        call_args = mock_generator.call_args[0][0]
        
        # Verify prompt structure
        assert "Explain the correct answer" in call_args
        assert "What is Python?" in call_args
        assert "Provide a short and clear explanation" in call_args
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_empty_quiz(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test explanation generation with empty quiz text"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "No explanation available"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations("")
        
        # Should still call generator (with empty extracted question)
        assert isinstance(result, str)
        mock_generator.assert_called_once()
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_with_asterisk(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test explanation generation when correct answer is marked with asterisk"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "AI stands for Artificial Intelligence."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(SAMPLE_QUESTION_WITH_ASTERISK)
        
        # Should extract and process the question with asterisk
        call_args = mock_generator.call_args[0][0]
        assert "Artificial Intelligence (*)" in call_args
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_return_type(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that explanation returns a string"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "This is an explanation."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generate_explanation_multiple_questions(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that only the first question is explained"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "NLP explanation only"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        # Check that only question 1 is in the prompt
        call_args = mock_generator.call_args[0][0]
        assert "What does NLP stand for?" in call_args
        assert "What is machine learning?" not in call_args


class TestGenerateExplanationsIntegration:
    """Integration tests for generate_explanations with extract_first_question"""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_full_flow_extraction_to_explanation(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test complete flow from quiz text to explanation"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Python is a high-level programming language."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        # Full flow
        quiz_text = SAMPLE_SINGLE_QUESTION
        explanation = quiz_ai.generate_explanations(quiz_text)
        
        # Verify the flow worked
        assert "programming language" in explanation.lower()
        
        # Verify the prompt contained the extracted question
        call_args = mock_generator.call_args[0][0]
        assert "What is Python?" in call_args
        assert "a) A snake" in call_args
        assert "d) A movie" in call_args
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_explanation_handles_complex_formatting(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test explanation with complex formatted questions"""
        from phases.quiz_generator import QuizAI
        
        complex_quiz = """
1. Which statement is TRUE regarding neural 
   networks and their applications?
   
a) They require minimal training data
b) They excel at pattern recognition tasks
c) They always outperform traditional algorithms
d) They don't require feature engineering ever
"""
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Neural networks are good at pattern recognition."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        explanation = quiz_ai.generate_explanations(complex_quiz)
        
        # Should handle the complex formatting
        assert isinstance(explanation, str)
        call_args = mock_generator.call_args[0][0]
        assert "neural" in call_args.lower()


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_quiz_with_no_options(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test with quiz text that has no options"""
        from phases.quiz_generator import QuizAI
        
        quiz_text = "1. What is AI?\n\n2. What is ML?"
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "AI is artificial intelligence."}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(quiz_text)
        
        # Should still work, even without proper options
        assert isinstance(result, str)
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_quiz_with_extra_whitespace(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test with excessive whitespace in quiz text"""
        from phases.quiz_generator import QuizAI
        
        quiz_text = """
        
        
1.    What is Python?    


a)   A snake   
b)   A programming language   


c)   A type of food


d)   A movie


"""
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Python explanation"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(quiz_text)
        
        # Should handle extra whitespace
        assert isinstance(result, str)
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_quiz_with_unicode_characters(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test with unicode characters in quiz"""
        from phases.quiz_generator import QuizAI
        
        quiz_text = """
1. What is the concept of 'résumé' in ML?
a) A summary document
b) A type of neural network 🧠
c) Data preprocessing technique
d) None of the above
"""
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Explanation with émojis 🎉"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(quiz_text)
        
        # Should handle unicode
        assert isinstance(result, str)
        assert "émojis" in result or "Explanation" in result
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generator_returns_empty_string(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test when generator returns empty string"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": ""}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        # Should return empty string without error
        assert result == ""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_generator_returns_unexpected_format(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test when generator returns unexpected format"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        # Return unexpected structure (should cause KeyError if not handled)
        mock_generator.return_value = [{"wrong_key": "some text"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        # Should raise KeyError or be handled
        with pytest.raises(KeyError):
            quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_very_long_quiz_text(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test with very long quiz text"""
        from phases.quiz_generator import QuizAI
        
        # Create a very long quiz
        long_quiz = "1. " + ("What is this? " * 1000) + "\n"
        long_quiz += "a) Option A\nb) Option B\nc) Option C\nd) Option D"
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Long explanation"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        result = quiz_ai.generate_explanations(long_quiz)
        
        # Should handle long text
        assert isinstance(result, str)


class TestPromptConstruction:
    """Test prompt construction for the generator"""
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_prompt_contains_all_required_elements(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that prompt has all required elements"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Test"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        quiz_ai.generate_explanations(SAMPLE_QUIZ_TEXT)
        
        prompt = mock_generator.call_args[0][0]
        
        # Check for key prompt elements
        assert "Explain the correct answer" in prompt
        assert "multiple-choice question" in prompt
        assert "Question:" in prompt
        assert "short and clear explanation" in prompt
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForSeq2SeqLM')
    @patch('transformers.pipeline')
    def test_prompt_includes_extracted_question(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test that extracted question is included in prompt"""
        from phases.quiz_generator import QuizAI
        
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Test"}]
        
        quiz_ai = QuizAI()
        quiz_ai.generator = mock_generator
        
        quiz_ai.generate_explanations(SAMPLE_SINGLE_QUESTION)
        
        prompt = mock_generator.call_args[0][0]
        
        # Should include the question and all options
        assert "What is Python?" in prompt
        assert "a) A snake" in prompt
        assert "b) A programming language" in prompt
        assert "c) A type of food" in prompt
        assert "d) A movie" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])