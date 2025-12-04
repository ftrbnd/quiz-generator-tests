import pytest
from unittest.mock import patch
import gradio as gr

from src.phases.quizzes import Quiz

class TestQuizAnalysis:
    @pytest.fixture
    def quiz_instance(self):
        return Quiz()
    
    @pytest.fixture
    def sample_input_text(self):
        """Fixture providing sample input text"""
        return """
        Python is a high-level programming language. Guido van Rossum created Python in 1991.
        Python is widely used for web development, data science, and artificial intelligence.
        Many companies like Google and Microsoft use Python extensively.
        """
    
    @pytest.fixture
    def mock_algorithm_outputs(self):
        """Fixture providing mock outputs for algorithm functions"""
        return {
            'keywords': ['python', 'programming', 'language', 'development', 'data'],
            'entities': [
                {'text': 'Python', 'label': 'PRODUCT'},
                {'text': 'Guido van Rossum', 'label': 'PERSON'},
                {'text': '1991', 'label': 'DATE'},
                {'text': 'Google', 'label': 'ORG'},
                {'text': 'Microsoft', 'label': 'ORG'}
            ],
            'topics': [
                ['python', 'programming', 'language', 'development', 'web'],
                ['data', 'science', 'artificial', 'intelligence', 'companies'],
                ['google', 'microsoft', 'use', 'extensively', 'created']
            ]
        }
    
    def test_analyze_without_input_text(self, quiz_instance):
        """Test analyze when no input text has been set"""
        # Set empty input text
        quiz_instance.input_text = ''
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = []
            mock_topics.return_value = []
            
            result = quiz_instance.analyze()
            
            # Verify functions were called with empty text
            mock_keywords.assert_called_once_with('', top_n=10)
            mock_entities.assert_called_once_with('')
            mock_topics.assert_called_once_with('', n_topics=3)
    
    def test_analyze_returns_correct_output_format(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze returns the correct tuple with three Gradio components"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = "# Original Quiz\n\n"
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            result = quiz_instance.analyze()
        
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
    
    def test_analyze_appends_to_existing_markdown(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze appends analysis to existing markdown_result"""
        original_markdown = "# Generated Quiz\n\n**Q1.** Test question?\n\n"
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = original_markdown
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            quiz_instance.analyze()
        
        # Verify original content is still present
        assert original_markdown in quiz_instance.markdown_result
        
        # Verify analysis section is added
        assert "## Analysis" in quiz_instance.markdown_result
        assert quiz_instance.markdown_result.startswith(original_markdown)
    
    def test_analyze_includes_keywords_section(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze includes TF-IDF keywords in the output"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = []
            mock_topics.return_value = []
            
            result = quiz_instance.analyze()
        
        # Verify keywords are in the markdown
        _, _, markdown_output = result
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        
        assert "Key Terms (TF-IDF):" in quiz_instance.markdown_result
        for keyword in mock_algorithm_outputs['keywords']:
            assert keyword in quiz_instance.markdown_result
    
    def test_analyze_includes_entities_section(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze includes named entities in the output"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = []
            
            result = quiz_instance.analyze()
        
        # Verify entities are in the markdown
        assert "Named Entities (NER):" in quiz_instance.markdown_result
        assert "Guido van Rossum (PERSON)" in quiz_instance.markdown_result
        assert "Google (ORG)" in quiz_instance.markdown_result
        assert "Microsoft (ORG)" in quiz_instance.markdown_result
    
    def test_analyze_includes_topics_section(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze includes LDA topics in the output"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = []
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            result = quiz_instance.analyze()
        
        # Verify topics are in the markdown
        assert "Topics (LDA):" in quiz_instance.markdown_result
        assert "Topic 1:" in quiz_instance.markdown_result
        assert "Topic 2:" in quiz_instance.markdown_result
        assert "Topic 3:" in quiz_instance.markdown_result
        
        # Verify some topic words are present
        assert "python" in quiz_instance.markdown_result
        assert "programming" in quiz_instance.markdown_result
    
    def test_analyze_handles_empty_entities(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze handles empty entities list correctly"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = []  # Empty entities
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            result = quiz_instance.analyze()
        
        # Verify that Named Entities section is NOT included when empty
        assert "Named Entities (NER):" not in quiz_instance.markdown_result
        
        # But other sections should still be there
        assert "Key Terms (TF-IDF):" in quiz_instance.markdown_result
        assert "Topics (LDA):" in quiz_instance.markdown_result
    
    def test_analyze_handles_empty_topics(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that analyze handles empty topics list correctly"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = []  # Empty topics
            
            result = quiz_instance.analyze()
        
        # Verify that Topics section is NOT included when empty
        assert "Topics (LDA):" not in quiz_instance.markdown_result
        
        # But other sections should still be there
        assert "Key Terms (TF-IDF):" in quiz_instance.markdown_result
        assert "Named Entities (NER):" in quiz_instance.markdown_result
    
    def test_analyze_limits_entities_to_ten(self, quiz_instance, sample_input_text):
        """Test that analyze limits entities to 10 items"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        # Create more than 10 entities
        many_entities = [
            {'text': f'Entity{i}', 'label': 'PERSON'} 
            for i in range(15)
        ]
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = many_entities
            mock_topics.return_value = []
            
            result = quiz_instance.analyze()
        
        # Count how many entities appear in the markdown
        # Should be max 10
        entity_count = sum(1 for i in range(15) if f'Entity{i}' in quiz_instance.markdown_result)
        assert entity_count <= 10
    
    def test_analyze_limits_topics_words_to_five(self, quiz_instance, sample_input_text):
        """Test that analyze limits topic words to 5 per topic"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        # Create topics with more than 5 words each
        topics_with_many_words = [
            ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8']
        ]
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = []
            mock_topics.return_value = topics_with_many_words
            
            result = quiz_instance.analyze()
        
        # Verify only first 5 words appear
        for i in range(1, 6):
            assert f'word{i}' in quiz_instance.markdown_result
        
        # Words 6-8 should not appear
        for i in range(6, 9):
            assert f'word{i}' not in quiz_instance.markdown_result
    
    def test_analyze_calls_algorithms_with_correct_parameters(self, quiz_instance, sample_input_text):
        """Test that analyze calls algorithm functions with correct parameters"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = ""
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = []
            mock_entities.return_value = []
            mock_topics.return_value = []
            
            quiz_instance.analyze()
            
            # Verify correct function calls
            mock_keywords.assert_called_once_with(sample_input_text, top_n=10)
            mock_entities.assert_called_once_with(sample_input_text)
            mock_topics.assert_called_once_with(sample_input_text, n_topics=3)
    
    def test_analyze_complete_workflow(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test complete analyze workflow with all sections"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = "# Quiz\n\n"
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            result = quiz_instance.analyze()
        
        # Verify all sections are present
        assert "## Analysis" in quiz_instance.markdown_result
        assert "Key Terms (TF-IDF):" in quiz_instance.markdown_result
        assert "Named Entities (NER):" in quiz_instance.markdown_result
        assert "Topics (LDA):" in quiz_instance.markdown_result
        
        # Verify separator is present
        assert "---" in quiz_instance.markdown_result
        
        # Verify result format
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_analyze_multiple_calls_appends_multiple_times(self, quiz_instance, sample_input_text, mock_algorithm_outputs):
        """Test that calling analyze multiple times appends multiple analysis sections"""
        quiz_instance.input_text = sample_input_text
        quiz_instance.markdown_result = "# Quiz\n\n"
        
        with patch('src.phases.algorithms.extract_keywords_tfidf') as mock_keywords, \
             patch('src.phases.algorithms.extract_entities_ner') as mock_entities, \
             patch('src.phases.algorithms.extract_topics_lda') as mock_topics:
            
            mock_keywords.return_value = mock_algorithm_outputs['keywords']
            mock_entities.return_value = mock_algorithm_outputs['entities']
            mock_topics.return_value = mock_algorithm_outputs['topics']
            
            # Call analyze twice
            quiz_instance.analyze()
            first_length = len(quiz_instance.markdown_result)
            
            quiz_instance.analyze()
            second_length = len(quiz_instance.markdown_result)
        
        # Second call should have appended more content
        assert second_length > first_length
        
        # Should have multiple Analysis sections
        assert quiz_instance.markdown_result.count("## Analysis") == 2