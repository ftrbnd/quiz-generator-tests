import pytest
from unittest.mock import patch
import gradio as gr

from phases.quizzes import Quiz 

class TestQuizShuffling:
    @pytest.fixture
    def quiz_instance(self):
        return Quiz()
    
    @pytest.fixture
    def sample_questions(self):
        return [
            {
                'question': 'The capital of France is _____.',
                'answer': 'Paris',
                'type': 'fill_blank'
            },
            {
                'question': 'Python was created by _____ in 1991.',
                'answer': 'Guido van Rossum',
                'type': 'fill_blank'
            },
            {
                'question': 'The speed of light is approximately _____ m/s.',
                'answer': '300,000,000',
                'type': 'fill_blank'
            },
            {
                'question': 'Water boils at _____ degrees Celsius.',
                'answer': '100',
                'type': 'fill_blank'
            }
        ]
    
    def test_shuffle_with_empty_questions(self, quiz_instance):
        """Test shuffling when no questions exist in quiz state"""
        result = quiz_instance.shuffle()

        assert isinstance(result, tuple) 
        assert result[2] == "Please generate a quiz first before shuffling!"
    
    def test_shuffle_with_uninitialized_state(self, quiz_instance):
        """Test shuffling when quiz state is empty"""
        quiz_instance.current_quiz_state['questions'] = []
        result = quiz_instance.shuffle()
        
        assert isinstance(result, tuple) 
        assert result[2] == "Please generate a quiz first before shuffling!"
    
    def test_shuffle_maintains_question_count(self, quiz_instance, sample_questions):
        """Test that shuffling maintains the same number of questions"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        with patch('random.shuffle') as mock_shuffle:
            quiz_instance.shuffle()
            
            # Verify shuffle was called
            assert mock_shuffle.called
            
            # Get the list that was passed to shuffle
            shuffled_list = mock_shuffle.call_args[0][0]
            assert len(shuffled_list) == len(sample_questions)
    
    def test_shuffle_contains_all_original_questions(self, quiz_instance, sample_questions):
        """Test that shuffled quiz contains all original questions"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        # Get the original question texts
        original_questions = {q['question'] for q in sample_questions}
        original_answers = {q['answer'] for q in sample_questions}
        
        # Mock random.shuffle to reverse the list (deterministic shuffle for testing)
        with patch('random.shuffle', side_effect=lambda x: x.reverse()):
            result = quiz_instance.shuffle()
        
        # Extract the markdown output
        _, _, markdown_output = result
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        # Verify all questions and answers are present
        for question_text in original_questions:
            assert question_text in markdown_text
        for answer in original_answers:
            assert answer in markdown_text
    
    def test_shuffle_returns_correct_output_format(self, quiz_instance, sample_questions):
        """Test that shuffle returns the correct Gradio components tuple"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        result = quiz_instance.shuffle()
        
        # Should return a tuple of (gr.update, gr.update, gr.Markdown)
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        # First element should be a dict with visible=True
        gradio_update = result[0]
        assert isinstance(gradio_update, dict)
        assert gradio_update.get('visible') is True

        # Second element should be a dict with visible=True
        gradio_update = result[1]
        assert isinstance(gradio_update, dict)
        assert gradio_update.get('visible') is True
        
        # Third element should be a Gradio Markdown component
        markdown_output = result[2]
        assert isinstance(markdown_output, gr.Markdown)
    
    def test_shuffle_does_not_modify_original_state(self, quiz_instance, sample_questions):
        """Test that shuffling doesn't modify the original question order in state"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        # Store original order
        original_order = [q['question'] for q in quiz_instance.current_quiz_state['questions']]
        
        # Shuffle
        quiz_instance.shuffle()
        
        # Verify original state is unchanged
        current_order = [q['question'] for q in quiz_instance.current_quiz_state['questions']]
        assert current_order == original_order
    
    @patch('random.shuffle')
    def test_shuffle_calls_random_shuffle(self, mock_shuffle, quiz_instance, sample_questions):
        """Test that shuffle() actually calls random.shuffle"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        quiz_instance.shuffle()
        
        assert mock_shuffle.called
        assert mock_shuffle.call_count == 1
    
    def test_shuffle_creates_copy_of_questions(self, quiz_instance, sample_questions):
        """Test that shuffle works on a copy, not the original list"""
        quiz_instance.current_quiz_state['questions'] = sample_questions
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        with patch('random.shuffle') as mock_shuffle:
            quiz_instance.shuffle()
            
            # Get the shuffled list
            shuffled_list = mock_shuffle.call_args[0][0]
            
            # Verify it's not the same object reference
            assert shuffled_list is not quiz_instance.current_quiz_state['questions']
    
    def test_shuffle_output_contains_correct_question_count(self, quiz_instance, sample_questions):
        """Test that the markdown output shows the correct question count"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        result = quiz_instance.shuffle()
        _, _, markdown_output = result
        
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        # Check that the header contains the correct count
        assert f"Generated Quiz ({len(sample_questions)} questions)" in markdown_text
    
    def test_shuffle_multiple_times_produces_valid_output(self, quiz_instance, sample_questions):
        """Test that shuffling multiple times always produces valid output"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        # Shuffle multiple times
        for _ in range(5):
            result = quiz_instance.shuffle()
            
            # Verify each result is valid
            assert isinstance(result, tuple)
            assert len(result) == 3
            
            gradio_update_1, gradio_update_2, markdown_output = result
            assert gradio_update_1.get('visible') is True
            assert gradio_update_2.get('visible') is True
            assert isinstance(markdown_output, gr.Markdown)
    
    def test_shuffle_with_single_question(self, quiz_instance):
        """Test shuffling with only one question"""
        single_question = [
            {
                'question': 'The capital of France is _____.',
                'answer': 'Paris',
                'type': 'fill_blank'
            }
        ]
        
        quiz_instance.current_quiz_state['questions'] = single_question.copy()
        quiz_instance.current_quiz_state['num_questions'] = 1
        
        result = quiz_instance.shuffle()
        
        # Should still work and return valid output
        assert isinstance(result, tuple)
        _, _, markdown_output = result
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        assert 'The capital of France is _____.' in markdown_text
    
    def test_shuffle_preserves_question_structure(self, quiz_instance, sample_questions):
        """Test that shuffled questions maintain their dictionary structure"""
        quiz_instance.current_quiz_state['questions'] = sample_questions.copy()
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        
        with patch('random.shuffle', side_effect=lambda x: x.reverse()):
            result = quiz_instance.shuffle()
        
        _, _, markdown_output = result
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        # Verify all required fields are present in output
        for question in sample_questions:
            assert question['question'] in markdown_text
            assert question['answer'] in markdown_text