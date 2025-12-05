import pytest
from unittest.mock import patch, mock_open, MagicMock
import csv
from io import StringIO

from phases.quizzes import Quiz 

class TestQuizFileFormats:
    @pytest.fixture
    def quiz_instance(self):
        return Quiz()
    
    @pytest.fixture
    def sample_questions(self):
        return [
            {
                'question': 'Python is a high-level _____ language.',
                'answer': 'programming',
                'type': 'fill_blank'
            },
            {
                'question': 'What is Python?',
                'answer': 'A programming language',
                'options': ['A) A programming language', 'B) A snake', 'C) A framework'],
                'type': 'mcq'
            },
            {
                'question': 'Explain the concept of object-oriented programming.',
                'answer': 'OOP is a programming paradigm',
                'type': 'topic'
            }
        ]
    
    @pytest.fixture
    def setup_quiz_with_questions(self, quiz_instance, sample_questions):
        """Setup quiz instance with sample questions"""
        quiz_instance.current_quiz_state['questions'] = sample_questions
        quiz_instance.current_quiz_state['num_questions'] = len(sample_questions)
        quiz_instance.markdown_result = "# Sample Quiz\n\n**Q1.** Test question?"
        return quiz_instance
    
    def test_download_markdown_format(self, setup_quiz_with_questions):
        """Test downloading quiz in Markdown format"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()) as mock_file:
            filename, markdown_output = quiz.download("md")
            
            assert filename == "generated_quiz.md"
            mock_file.assert_called_once_with("generated_quiz.md", "w", encoding='utf-8')
            
            # Verify markdown content was written
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            assert "# Sample Quiz" in written_content
    
    def test_download_csv_format(self, setup_quiz_with_questions):
        """Test downloading quiz in CSV format"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()) as mock_file:
            filename, markdown_output = quiz.download("csv")
            
            assert filename == "generated_quiz.csv"
            mock_file.assert_called_once()
            
            # Verify CSV content
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            # Parse CSV to verify structure
            csv_reader = csv.reader(StringIO(written_content))
            rows = list(csv_reader)
            
            # Check header
            assert rows[0] == ['Question Number', 'Type', 'Question', 'Answer', 'Options']
            assert len(rows) == 4  # Header + 3 questions
    
    def test_download_txt_format(self, setup_quiz_with_questions):
        """Test downloading quiz in plain text format"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()) as mock_file:
            filename, markdown_output = quiz.download("txt")
            
            assert filename == "generated_quiz.txt"
            mock_file.assert_called_once_with("generated_quiz.txt", "w", encoding='utf-8')
            
            # Verify text content
            handle = mock_file()
            written_content = handle.write.call_args[0][0]
            
            assert "Generated Quiz" in written_content
            assert "Q1." in written_content
            assert "Answer:" in written_content
    
    def test_download_pdf_format(self, setup_quiz_with_questions):
        """Test downloading quiz in PDF format"""
        quiz = setup_quiz_with_questions
        
        with patch('phases.quizzes.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = MagicMock()
            mock_doc.return_value = mock_doc_instance
            
            filename, markdown_output = quiz.download("pdf")
            
            assert filename == "generated_quiz.pdf"
            mock_doc_instance.build.assert_called_once()
    
    def test_download_with_empty_questions(self, quiz_instance):
        """Test download with no questions"""
        quiz_instance.current_quiz_state['questions'] = []
        quiz_instance.markdown_result = ""
        
        filename, markdown_output = quiz_instance.download("md")
        
        assert filename is None
        markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
        assert "No quiz to download" in markdown_text
    
    def test_download_with_invalid_file_type(self, setup_quiz_with_questions):
        """Test download with invalid file type defaults to markdown"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()) as mock_file:
            filename, _ = quiz.download("invalid")
            
            # Should default to markdown
            assert filename == "generated_quiz.md"
    
    def test_download_success_message(self, setup_quiz_with_questions):
        """Test that download returns success message"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()):
            filename, markdown_output = quiz.download("md")
            
            markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
            assert "Quiz downloaded" in markdown_text
            assert "generated_quiz.md" in markdown_text
    
    def test_download_handles_exceptions(self, setup_quiz_with_questions):
        """Test that download handles file write errors gracefully"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', side_effect=IOError("Disk full")):
            filename, markdown_output = quiz.download("md")
            
            assert filename is None
            markdown_text = markdown_output.value if hasattr(markdown_output, 'value') else str(markdown_output)
            assert "Error downloading quiz" in markdown_text
            assert "Disk full" in markdown_text
    
    def test_format_as_csv_with_mcq_options(self, setup_quiz_with_questions):
        """Test CSV formatting properly handles MCQ options"""
        quiz = setup_quiz_with_questions
        questions = quiz.current_quiz_state['questions']
        
        csv_content = quiz.format_as_csv(questions)
        csv_reader = csv.reader(StringIO(csv_content))
        rows = list(csv_reader)
        
        # Find the MCQ row
        mcq_row = None
        for row in rows[1:]:
            if row[1] == 'mcq':
                mcq_row = row
                break
        
        assert mcq_row is not None
        assert '|' in mcq_row[4]  # Options are pipe-separated
        assert 'A) A programming language' in mcq_row[4]
    
    def test_format_as_txt_structure(self, setup_quiz_with_questions):
        """Test plain text formatting structure"""
        quiz = setup_quiz_with_questions
        questions = quiz.current_quiz_state['questions']
        
        txt_content = quiz.format_as_txt(questions)
        
        assert "Generated Quiz" in txt_content
        assert "=" in txt_content  # Title separator
        assert "-" in txt_content  # Question separator
        assert "[Fill Blank]" in txt_content or "Fill Blank" in txt_content
        assert "[Mcq]" in txt_content or "Mcq" in txt_content
    
    def test_clean_text_for_pdf(self, quiz_instance):
        """Test PDF text cleaning function"""
        # Test markdown bold/italic
        text = "This is **bold** and *italic* text"
        cleaned = quiz_instance._clean_text_for_pdf(text)
        assert '<b>bold</b>' in cleaned
        assert '<i>italic</i>' in cleaned
        
        # Test blanks
        text = "Fill in the _____"
        cleaned = quiz_instance._clean_text_for_pdf(text)
        assert '___________' in cleaned
        
        # Test XML escaping
        text = "Question with <tag> and & symbol"
        cleaned = quiz_instance._clean_text_for_pdf(text)
        assert '&lt;tag&gt;' in cleaned
        assert '&amp;' in cleaned
    
    def test_download_preserves_unicode(self, quiz_instance):
        """Test that all formats preserve unicode characters"""
        unicode_questions = [
            {
                'question': 'Python supports 你好 and émojis 🐍',
                'answer': 'unicode',
                'type': 'fill_blank'
            }
        ]
        
        quiz_instance.current_quiz_state['questions'] = unicode_questions
        quiz_instance.markdown_result = "Test"
        
        # Test CSV
        csv_content = quiz_instance.format_as_csv(unicode_questions)
        assert '你好' in csv_content
        assert '🐍' in csv_content
        
        # Test TXT
        txt_content = quiz_instance.format_as_txt(unicode_questions)
        assert '你好' in txt_content
        assert '🐍' in txt_content
    
    def test_download_all_formats_sequentially(self, setup_quiz_with_questions):
        """Test downloading all formats in sequence"""
        quiz = setup_quiz_with_questions
        formats = ["md", "csv", "txt", "pdf"]
        
        for file_format in formats:
            if file_format == "pdf":
                with patch('phases.quizzes.SimpleDocTemplate'):
                    filename, _ = quiz.download(file_format)
            else:
                with patch('builtins.open', mock_open()):
                    filename, _ = quiz.download(file_format)
            
            # Verify correct filename extension
            assert filename.endswith(f".{file_format}")
    
    def test_csv_newline_parameter(self, setup_quiz_with_questions):
        """Test that CSV uses newline='' parameter"""
        quiz = setup_quiz_with_questions
        
        with patch('builtins.open', mock_open()) as mock_file:
            quiz.download("csv")
            
            # Verify newline parameter is set
            call_kwargs = mock_file.call_args[1]
            assert call_kwargs.get('newline') == ''