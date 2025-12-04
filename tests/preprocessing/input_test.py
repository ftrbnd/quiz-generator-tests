import pytest
from unittest.mock import patch
import gradio as gr

from src.phases.quizzes import Quiz  # Adjust import path as needed

class TestInputValidation:
    @pytest.fixture
    def quiz_instance(self):
        """Fixture providing a fresh Quiz instance for each test"""
        return Quiz()
    
    @pytest.fixture
    def sample_input_text(self):
        """Fixture providing sample input text"""
        return """
        Python is a high-level programming language. Guido van Rossum created Python in 1991.
        Python is widely used for web development, data science, and artificial intelligence.
        The Python Software Foundation manages the development of Python.
        """
    
    @pytest.fixture
    def sample_generated_questions(self):
        """Fixture providing sample generated questions"""
        return [
            {
                'question': 'Python is a high-level _____ language.',
                'answer': 'programming',
                'type': 'fill_blank'
            },
            {
                'question': '_____ created Python in 1991.',
                'answer': 'Guido van Rossum',
                'type': 'fill_blank'
            },
            {
                'question': 'Python is widely used for web development, _____, and artificial intelligence.',
                'answer': 'data science',
                'type': 'fill_blank'
            }
        ]
    
    def test_generate_with_empty_input(self, quiz_instance):
        """Test generation with empty input text"""
        result = quiz_instance.generate_from_text("", 5, ['fill_blank'])
        
        assert isinstance(result, tuple)
        assert result[2] == "Please provide text to generate questions from."
    
    def test_generate_with_whitespace_only(self, quiz_instance):
        """Test generation with whitespace-only input"""
        result = quiz_instance.generate_from_text("   \n\t  ", 5, ['fill_blank'])
        
        assert isinstance(result, tuple)
        assert result[2] == "Please provide text to generate questions from."
    
    def test_generate_with_none_input(self, quiz_instance):
        """Test generation with None input"""
        # This should raise an AttributeError since None doesn't have .strip()
        with pytest.raises(AttributeError):
            quiz_instance.generate_from_text(None, 5, ['fill_blank'])
    
    def test_generate_returns_correct_output_format(self, quiz_instance, sample_input_text, sample_generated_questions):
        """Test that generate_from_text returns the correct tuple format"""
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = sample_generated_questions
            
            result = quiz_instance.generate_from_text(sample_input_text, 3, ['fill_blank'])
        
        # Should return a tuple of (gr.update, gr.update, gr.Markdown)
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        # First two elements should be dicts with visible=True
        gradio_update_1 = result[0]
        gradio_update_2 = result[1]
        assert isinstance(gradio_update_1, dict)
        assert isinstance(gradio_update_2, dict)
        assert gradio_update_1.get('visible') is True
        assert gradio_update_2.get('visible') is True
        
        # Third element should be a Gradio Markdown component
        markdown_output = result[2]
        assert isinstance(markdown_output, gr.Markdown)
    
    def test_generate_stores_input_text(self, quiz_instance, sample_input_text, sample_generated_questions):
        """Test that generate_from_text stores the input text in instance variable"""
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = sample_generated_questions
            
            quiz_instance.generate_from_text(sample_input_text, 3, ['fill_blank'])
        
        # Verify input text is stored
        assert quiz_instance.input_text == sample_input_text
    
    def test_generate_updates_quiz_state(self, quiz_instance, sample_input_text, sample_generated_questions):
        """Test that generate_from_text updates the quiz state correctly"""
        num_questions = 3
        question_types = ['fill_blank']
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = sample_generated_questions
            
            quiz_instance.generate_from_text(sample_input_text, num_questions, question_types)
        
        # Verify quiz state is updated
        assert quiz_instance.current_quiz_state['questions'] == sample_generated_questions
        assert quiz_instance.current_quiz_state['num_questions'] == num_questions
        assert quiz_instance.current_quiz_state['question_types'] == question_types
    
    
    def test_generate_with_various_input_lengths(self, quiz_instance):
        """Test generation with different input text lengths"""
        test_cases = [
            ("Short text.", 1),
            ("Medium length text with multiple sentences. Here is another one. And one more.", 3),
            ("Very long text. " * 50, 10)
        ]
        
        for input_text, num_questions in test_cases:
            with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
                mock_generate.return_value = [{'question': 'Q', 'answer': 'A', 'type': 'fill_blank'}]
                
                result = quiz_instance.generate_from_text(input_text, num_questions, ['fill_blank'])
                
                assert isinstance(result, tuple)
                assert quiz_instance.input_text == input_text
    
    def test_generate_with_special_characters_in_input(self, quiz_instance):
        """Test generation with special characters in input text"""
        special_text = """
        Python's syntax is clean & simple! It uses "indentation" for blocks.
        Common operators: +, -, *, /, %, //, **, ==, !=, <, >, <=, >=
        String formatting: f"{variable}" or "{}".format(value)
        """
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = [
                {'question': 'Test _____ question?', 'answer': 'special', 'type': 'fill_blank'}
            ]
            
            result = quiz_instance.generate_from_text(special_text, 1, ['fill_blank'])
        
        # Verify it handles special characters
        assert isinstance(result, tuple)
        assert quiz_instance.input_text == special_text
    
    def test_generate_with_unicode_characters(self, quiz_instance):
        """Test generation with unicode characters in input"""
        unicode_text = """
        Python supports Unicode: 你好世界, Привет мир, مرحبا بالعالم
        Emoji support: 🐍 Python 🚀 Programming 💻
        Mathematical symbols: α, β, γ, ∞, ∑, ∫
        """
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = [
                {'question': 'Unicode _____ test', 'answer': 'characters', 'type': 'fill_blank'}
            ]
            
            result = quiz_instance.generate_from_text(unicode_text, 1, ['fill_blank'])
        
        assert isinstance(result, tuple)
        assert quiz_instance.input_text == unicode_text
    
    def test_generate_with_multiline_input(self, quiz_instance):
        """Test generation with input containing multiple paragraphs"""
        multiline_text = """
        First paragraph with important information about Python.
        
        Second paragraph discussing data structures and algorithms.
        
        Third paragraph about web frameworks like Django and Flask.
        
        Fourth paragraph covering testing and best practices.
        """
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = [
                {'question': 'Test _____?', 'answer': 'question', 'type': 'fill_blank'}
            ]
            
            result = quiz_instance.generate_from_text(multiline_text, 1, ['fill_blank'])
        
        assert isinstance(result, tuple)
        assert quiz_instance.input_text == multiline_text
    
    def test_generate_preserves_input_formatting(self, quiz_instance):
        """Test that input text formatting is preserved in storage"""
        formatted_text = "Line 1\n\tIndented line\n  Spaces\nLine 4"
        
        with patch('src.phases.quizzes.q_types.generate_fill_blank_questions') as mock_generate:
            mock_generate.return_value = []
            
            quiz_instance.generate_from_text(formatted_text, 1, ['fill_blank'])
        
        # Verify exact formatting is preserved
        assert quiz_instance.input_text == formatted_text