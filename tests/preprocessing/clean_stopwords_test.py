
import pytest
from unittest.mock import patch

class TestPreprocessText:
    """Test suite for preprocess_text function"""
    
    def test_single_sentence(self):
        """Test with a single sentence"""
        from phases.preprocessing import preprocess_text
        
        text = "This is a single sentence."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "This is a single sentence."
    
    def test_multiple_sentences(self):
        """Test with multiple sentences"""
        from phases.preprocessing import preprocess_text
        
        text = "This is the first sentence. This is the second sentence. Here is a third one."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == "This is the first sentence."
        assert result[1] == "This is the second sentence."
        assert result[2] == "Here is a third one."
    
    def test_empty_string(self):
        """Test with empty string"""
        from phases.preprocessing import preprocess_text
        
        text = ""
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_whitespace_only(self):
        """Test with whitespace only"""
        from phases.preprocessing import preprocess_text
        
        text = "   \n\n\t  "
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # NLTK may return empty list or list with whitespace
        # Both are acceptable behaviors
        assert len(result) <= 1
    
    def test_sentence_with_abbreviations(self):
        """Test sentences with abbreviations (Dr., Mr., etc.)"""
        from phases.preprocessing import preprocess_text
        
        text = "Dr. Smith went to the store. He bought milk."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # NLTK should handle abbreviations correctly
        assert len(result) == 2
        assert "Dr. Smith went to the store." in result[0]
    
    def test_sentence_with_numbers(self):
        """Test sentences with decimal numbers"""
        from phases.preprocessing import preprocess_text
        
        text = "The price is $19.99. That's a good deal."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "$19.99" in result[0]
    
    def test_multiple_punctuation(self):
        """Test with multiple punctuation marks"""
        from phases.preprocessing import preprocess_text
        
        text = "What?! This is amazing! Really?"
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) >= 1
        # Should split on different punctuation marks
    
    def test_newlines_and_paragraphs(self):
        """Test with newlines and paragraph breaks"""
        from phases.preprocessing import preprocess_text
        
        text = "First sentence.\n\nSecond sentence in new paragraph.\nThird sentence."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_unicode_characters(self):
        """Test with unicode characters"""
        from phases.preprocessing import preprocess_text
        
        text = "This has émojis 🎉. And spëcial çharacters."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "émojis" in result[0]
        assert "🎉" in result[0]
    
    def test_quoted_sentences(self):
        """Test with quoted text"""
        from phases.preprocessing import preprocess_text
        
        text = 'He said, "Hello there." She replied, "Hi!"'
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # NLTK should handle quotes appropriately
        assert len(result) >= 1
    
    def test_ellipsis(self):
        """Test sentences with ellipsis"""
        from phases.preprocessing import preprocess_text
        
        text = "Wait... What is that? I don't know."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) >= 2
    
    def test_long_paragraph(self):
        """Test with a long paragraph of text"""
        from phases.preprocessing import preprocess_text
        
        text = """
        Natural language processing is a subfield of linguistics, computer science, 
        and artificial intelligence. It is concerned with the interactions between 
        computers and human language. In particular, it focuses on how to program 
        computers to process and analyze large amounts of natural language data.
        """
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) >= 3
        # Check that sentences are properly extracted
        for sentence in result:
            assert isinstance(sentence, str)
            assert len(sentence) > 0
    
    def test_sentences_with_colons(self):
        """Test sentences with colons"""
        from phases.preprocessing import preprocess_text
        
        text = "Here's the list: apples, oranges, and bananas. They're fresh."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_mixed_case_sentences(self):
        """Test with mixed case text"""
        from phases.preprocessing import preprocess_text
        
        text = "THIS IS UPPERCASE. this is lowercase. This Is Mixed Case."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 3
        # Case should be preserved
        assert "THIS IS UPPERCASE." in result[0]
        assert "this is lowercase." in result[1]
    
    def test_sentences_with_urls(self):
        """Test sentences containing URLs"""
        from phases.preprocessing import preprocess_text
        
        text = "Visit https://example.com for more. It's a great site."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "https://example.com" in result[0]
    
    def test_sentences_with_emails(self):
        """Test sentences containing email addresses"""
        from phases.preprocessing import preprocess_text
        
        text = "Contact me at user@example.com. I'll respond quickly."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "user@example.com" in result[0]


class TestGetStopWords:
    """Test suite for get_stop_words function"""
    
    def test_returns_set(self):
        """Test that function returns a set"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        assert isinstance(result, set)
    
    def test_contains_common_stopwords(self):
        """Test that result contains common English stopwords"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        # Check for common stopwords
        common_stopwords = ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were']
        
        for word in common_stopwords:
            assert word in result, f"Expected stopword '{word}' not found"
    
    def test_not_empty(self):
        """Test that stopwords set is not empty"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        assert len(result) > 0
        # English stopwords should have at least 100 words
        assert len(result) > 100
    
    def test_lowercase_words(self):
        """Test that all stopwords are lowercase"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        for word in result:
            assert word.islower() or not word.isalpha(), \
                f"Stopword '{word}' is not lowercase"
    
    def test_consistency(self):
        """Test that function returns consistent results"""
        from phases.preprocessing import get_stop_words
        
        result1 = get_stop_words()
        result2 = get_stop_words()
        
        assert result1 == result2
        assert len(result1) == len(result2)
    
    def test_specific_stopwords_present(self):
        """Test for specific important stopwords"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        important_stopwords = [
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'this', 'that', 'these', 'those',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        ]
        
        missing = [word for word in important_stopwords if word not in result]
        assert len(missing) == 0, f"Missing stopwords: {missing}"
    
    def test_no_uppercase_stopwords(self):
        """Test that there are no uppercase stopwords"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        uppercase_words = [word for word in result if word.isupper()]
        assert len(uppercase_words) == 0
    
    def test_no_punctuation_only(self):
        """Test that stopwords don't consist of only punctuation"""
        from phases.preprocessing import get_stop_words
        
        result = get_stop_words()
        
        for word in result:
            # Stopwords should contain at least one alphanumeric character
            assert any(c.isalnum() for c in word), \
                f"Stopword '{word}' contains no alphanumeric characters"
    
    def test_caching_behavior(self):
        """Test that multiple calls don't reload stopwords each time"""
        from phases.preprocessing import get_stop_words
        
        # Call multiple times
        results = [get_stop_words() for _ in range(5)]
        
        # All should be identical
        for result in results[1:]:
            assert result == results[0]


class TestNLTKDownload:
    """Test suite for NLTK data download logic"""
    
    @patch('nltk.data.find')
    @patch('nltk.download')
    def test_stopwords_already_downloaded(self, mock_download, mock_find):
        """Test when stopwords are already downloaded"""
        # Simulate stopwords already present
        mock_find.return_value = True
        
        # Re-import to trigger the download check
        import importlib
        import phases.preprocessing as prep
        importlib.reload(prep)
        
        # download should not be called
        mock_download.assert_not_called()
    
    @patch('nltk.data.find')
    @patch('nltk.download')
    def test_stopwords_not_downloaded(self, mock_download, mock_find):
        """Test when stopwords need to be downloaded"""
        # Simulate stopwords not present
        mock_find.side_effect = LookupError("Resource not found")
        mock_download.return_value = True
        
        # Re-import to trigger the download check
        import importlib
        import phases.preprocessing as prep
        importlib.reload(prep)
        
        # download should be called with 'stopwords'
        mock_download.assert_called_with('stopwords')


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_very_long_sentence(self):
        """Test with an extremely long sentence"""
        from phases.preprocessing import preprocess_text
        
        # Create a very long sentence (1000+ words)
        text = "This is a word. " * 500 + "Final sentence."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # Should handle long text without errors
        assert len(result) >= 1
    
    def test_special_characters_only(self):
        """Test with only special characters"""
        from phases.preprocessing import preprocess_text
        
        text = "!@#$%^&*()"
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # May return empty list or list with the characters
    
    def test_numbers_only_sentence(self):
        """Test with sentences containing only numbers"""
        from phases.preprocessing import preprocess_text
        
        text = "123 456 789. 10 11 12."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_mixed_languages(self):
        """Test with mixed language content"""
        from phases.preprocessing import preprocess_text
        
        text = "This is English. Esto es español. C'est français."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_html_like_text(self):
        """Test with HTML-like text"""
        from phases.preprocessing import preprocess_text
        
        text = "This is <b>bold</b>. This is <i>italic</i>."
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        # Should preserve HTML tags if present
        assert len(result) == 2
    
    def test_repeated_punctuation(self):
        """Test with repeated punctuation marks"""
        from phases.preprocessing import preprocess_text
        
        text = "What!!! Is this real??? Yes!!!"
        result = preprocess_text(text)
        
        assert isinstance(result, list)
        assert len(result) >= 2


class TestIntegration:
    """Integration tests combining both functions"""
    
    def test_preprocess_and_filter_stopwords(self):
        """Test preprocessing text and then filtering stopwords"""
        from phases.preprocessing import preprocess_text, get_stop_words
        
        text = "The quick brown fox jumps over the lazy dog. It is a test."
        sentences = preprocess_text(text)
        stopwords = get_stop_words()
        
        # Filter stopwords from each sentence
        filtered_sentences = []
        for sentence in sentences:
            words = sentence.lower().split()
            filtered = [word for word in words if word not in stopwords]
            filtered_sentences.append(filtered)
        
        assert len(filtered_sentences) == 2
        # 'the' should be filtered out
        assert 'the' not in filtered_sentences[0]
        # Content words should remain
        assert any('quick' in s for s in [' '.join(fs) for fs in filtered_sentences])
    
    def test_full_pipeline_example(self):
        """Test a complete text processing pipeline"""
        from phases.preprocessing import preprocess_text, get_stop_words
        
        text = """
        Natural language processing is important. It helps computers understand humans.
        This technology has many applications.
        """
        
        # Preprocess
        sentences = preprocess_text(text)
        assert len(sentences) >= 3
        
        # Get stopwords
        stopwords = get_stop_words()
        assert len(stopwords) > 0
        
        # Verify both functions work together
        for sentence in sentences:
            words = sentence.lower().split()
            content_words = [w for w in words if w not in stopwords]
            # Should have some content words remaining
            assert len(content_words) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])