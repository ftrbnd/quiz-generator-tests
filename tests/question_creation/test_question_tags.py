import pytest
import json
import os
from unittest.mock import patch, mock_open
import tempfile


# Sample test data
SAMPLE_QUESTION_BANK = [
    {
        "question": "What does NLP stand for?",
        "options": ["Natural Language Processing", "New Logic Principle", "Node Link Protocol", "Neural Language Path"],
        "correct_index": 0,
        "tags": ["NLP", "Basics"]
    },
    {
        "question": "What is overfitting in ML?",
        "options": ["Model too fitted to training data", "Lack of data", "Too many layers", "None"],
        "correct_index": 0,
        "tags": ["Machine Learning", "Modeling"]
    },
    {
        "question": "What is a neural network?",
        "options": ["A model inspired by the human brain", "A networking cable", "A file system", "None"],
        "correct_index": 0,
        "tags": ["Deep Learning", "Neural Networks"]
    }
]


class TestFilterByTag:
    """Test suite for filter_by_tag function"""
    
    def test_single_tag_filter(self):
        """Test filtering by a single tag"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["NLP"])
        
        assert len(result) == 1
        assert result[0]["question"] == "What does NLP stand for?"
        assert "NLP" in result[0]["tags"]
    
    def test_multiple_tags_filter(self):
        """Test filtering by multiple tags"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["NLP", "Machine Learning"])
        
        assert len(result) == 2
        questions = [q["question"] for q in result]
        assert "What does NLP stand for?" in questions
        assert "What is overfitting in ML?" in questions
    
    def test_filter_with_overlapping_tags(self):
        """Test filtering where questions have multiple matching tags"""
        from terminal.question_tags import filter_by_tag
        
        questions = [
            {"question": "Q1", "tags": ["A", "B"], "correct_index": 0, "options": []},
            {"question": "Q2", "tags": ["B", "C"], "correct_index": 0, "options": []},
            {"question": "Q3", "tags": ["C", "D"], "correct_index": 0, "options": []}
        ]
        
        result = filter_by_tag(questions, ["B", "C"])
        
        # Q1, Q2, and Q3 should all be included (no duplicates)
        assert len(result) == 3
    
    def test_no_matching_tags(self):
        """Test filtering with tags that don't match any questions"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["Nonexistent Tag"])
        
        assert len(result) == 0
    
    def test_empty_tag_list(self):
        """Test filtering with empty tag list"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag(SAMPLE_QUESTION_BANK, [])
        
        assert len(result) == 0
    
    def test_empty_question_bank(self):
        """Test filtering with empty question bank"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag([], ["NLP"])
        
        assert len(result) == 0
    
    def test_case_sensitive_tags(self):
        """Test that tag filtering is case-sensitive"""
        from terminal.question_tags import filter_by_tag
        
        # "nlp" (lowercase) should not match "NLP" (uppercase)
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["nlp"])
        
        assert len(result) == 0
    
    def test_partial_tag_matching(self):
        """Test that partial tag names don't match"""
        from terminal.question_tags import filter_by_tag
        
        # "NL" should not match "NLP"
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["NL"])
        
        assert len(result) == 0
    
    def test_all_questions_match(self):
        """Test when all questions match the filter"""
        from terminal.question_tags import filter_by_tag
        
        questions = [
            {"question": "Q1", "tags": ["Common"], "correct_index": 0, "options": []},
            {"question": "Q2", "tags": ["Common"], "correct_index": 0, "options": []},
            {"question": "Q3", "tags": ["Common"], "correct_index": 0, "options": []}
        ]
        
        result = filter_by_tag(questions, ["Common"])
        
        assert len(result) == 3
    
    def test_preserves_question_structure(self):
        """Test that filtering preserves complete question objects"""
        from terminal.question_tags import filter_by_tag
        
        result = filter_by_tag(SAMPLE_QUESTION_BANK, ["NLP"])
        
        assert len(result) == 1
        question = result[0]
        
        # Verify all fields are preserved
        assert "question" in question
        assert "options" in question
        assert "correct_index" in question
        assert "tags" in question
        assert len(question["options"]) == 4


class TestCalculateTagScores:
    """Test suite for calculate_tag_scores function"""
    
    def test_all_correct_answers(self):
        """Test scoring when all answers are correct"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = SAMPLE_QUESTION_BANK
        student_answers = [0, 0, 0]  # All correct
        
        result = calculate_tag_scores(questions, student_answers)
        
        assert "NLP" in result
        assert result["NLP"]["correct"] == 1
        assert result["NLP"]["total"] == 1
        
        assert "Machine Learning" in result
        assert result["Machine Learning"]["correct"] == 1
        assert result["Machine Learning"]["total"] == 1
    
    def test_all_wrong_answers(self):
        """Test scoring when all answers are wrong"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = SAMPLE_QUESTION_BANK
        student_answers = [1, 1, 1]  # All wrong
        
        result = calculate_tag_scores(questions, student_answers)
        
        assert "NLP" in result
        assert result["NLP"]["correct"] == 0
        assert result["NLP"]["total"] == 1
    
    def test_mixed_answers(self):
        """Test scoring with mixed correct and wrong answers"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = SAMPLE_QUESTION_BANK
        student_answers = [0, 1, 0]  # First and third correct
        
        result = calculate_tag_scores(questions, student_answers)
        
        assert result["NLP"]["correct"] == 1
        assert result["NLP"]["total"] == 1
        
        assert result["Machine Learning"]["correct"] == 0
        assert result["Machine Learning"]["total"] == 1
        
        assert result["Deep Learning"]["correct"] == 1
        assert result["Deep Learning"]["total"] == 1
    
    def test_multiple_tags_per_question(self):
        """Test that tags are properly counted when questions have multiple tags"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = [
            {
                "question": "Q1",
                "tags": ["Tag A", "Tag B"],
                "correct_index": 0,
                "options": []
            }
        ]
        student_answers = [0]  # Correct
        
        result = calculate_tag_scores(questions, student_answers)
        
        # Both tags should be credited
        assert result["Tag A"]["correct"] == 1
        assert result["Tag A"]["total"] == 1
        assert result["Tag B"]["correct"] == 1
        assert result["Tag B"]["total"] == 1
    
    def test_same_tag_multiple_questions(self):
        """Test accumulation for same tag across multiple questions"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = [
            {"question": "Q1", "tags": ["Common"], "correct_index": 0, "options": []},
            {"question": "Q2", "tags": ["Common"], "correct_index": 1, "options": []},
            {"question": "Q3", "tags": ["Common"], "correct_index": 0, "options": []}
        ]
        student_answers = [0, 0, 0]  # First and third correct, second wrong
        
        result = calculate_tag_scores(questions, student_answers)
        
        assert result["Common"]["correct"] == 2
        assert result["Common"]["total"] == 3
    
    def test_empty_questions(self):
        """Test with empty question list"""
        from terminal.question_tags import calculate_tag_scores
        
        result = calculate_tag_scores([], [])
        
        assert result == {}
    
    def test_tag_score_structure(self):
        """Test that tag score has correct structure"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = [SAMPLE_QUESTION_BANK[0]]
        student_answers = [0]
        
        result = calculate_tag_scores(questions, student_answers)
        
        # Each tag should have 'correct' and 'total' keys
        for tag, score in result.items():
            assert "correct" in score
            assert "total" in score
            assert isinstance(score["correct"], int)
            assert isinstance(score["total"], int)
            assert score["total"] >= score["correct"]


class TestGenerateTagReport:
    """Test suite for generate_tag_report function"""
    
    @patch('builtins.print')
    def test_report_generation(self, mock_print):
        """Test that report is generated with correct format"""
        from terminal.question_tags import generate_tag_report
        
        tag_scores = {
            "NLP": {"correct": 3, "total": 5},
            "Machine Learning": {"correct": 4, "total": 4}
        }
        
        generate_tag_report(tag_scores)
        
        # Verify print was called multiple times
        assert mock_print.call_count > 0
        
        # Check for header
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("TAG PERFORMANCE REPORT" in str(call) for call in print_calls)
    
    @patch('builtins.print')
    def test_report_accuracy_calculation(self, mock_print):
        """Test that accuracy is correctly calculated and formatted"""
        from terminal.question_tags import generate_tag_report
        
        tag_scores = {
            "Test Tag": {"correct": 3, "total": 4}
        }
        
        generate_tag_report(tag_scores)
        
        # Check that accuracy is displayed (75% in this case)
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("75.00%" in str(call) for call in print_calls)
    
    @patch('builtins.print')
    def test_report_empty_scores(self, mock_print):
        """Test report generation with empty scores"""
        from terminal.question_tags import generate_tag_report
        
        generate_tag_report({})
        
        # Should still print header
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("TAG PERFORMANCE REPORT" in str(call) for call in print_calls)
    
    @patch('builtins.print')
    def test_report_perfect_score(self, mock_print):
        """Test report with 100% accuracy"""
        from terminal.question_tags import generate_tag_report
        
        tag_scores = {
            "Perfect Tag": {"correct": 5, "total": 5}
        }
        
        generate_tag_report(tag_scores)
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("100.00%" in str(call) for call in print_calls)
    
    @patch('builtins.print')
    def test_report_zero_score(self, mock_print):
        """Test report with 0% accuracy"""
        from terminal.question_tags import generate_tag_report
        
        tag_scores = {
            "Failed Tag": {"correct": 0, "total": 5}
        }
        
        generate_tag_report(tag_scores)
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("0.00%" in str(call) for call in print_calls)
    
    @patch('builtins.print')
    def test_report_multiple_tags(self, mock_print):
        """Test report with multiple tags"""
        from terminal.question_tags import generate_tag_report
        
        tag_scores = {
            "Tag A": {"correct": 2, "total": 3},
            "Tag B": {"correct": 1, "total": 2},
            "Tag C": {"correct": 4, "total": 5}
        }
        
        generate_tag_report(tag_scores)
        
        # Should print info for all tags
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Tag A" in str(call) for call in print_calls)
        assert any("Tag B" in str(call) for call in print_calls)
        assert any("Tag C" in str(call) for call in print_calls)


class TestRunQuestionTags:
    """Test suite for run_question_tags function"""
    
    @patch('builtins.input', side_effect=["NLP,Basics", "0", "0"])
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    def test_run_with_valid_input(self, mock_file, mock_print, mock_input):
        """Test run_question_tags with valid user input"""
        from terminal.question_tags import run_question_tags
        
        run_question_tags()
        
        # Verify inputs were requested
        assert mock_input.call_count > 0
        
        # Verify file was written
        mock_file.assert_called()
    
    @patch('builtins.input', side_effect=["NLP", "0"])
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    def test_run_filters_questions(self, mock_file, mock_print, mock_input):
        """Test that questions are properly filtered by tags"""
        from terminal.question_tags import run_question_tags
        
        run_question_tags()
        
        # Check that filtered questions are displayed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("What does NLP stand for?" in str(call) for call in print_calls)
    
    @patch('builtins.input', side_effect=["InvalidTag", "0"])
    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    def test_run_with_no_matching_questions(self, mock_file, mock_print, mock_input):
        """Test behavior when no questions match the selected tags"""
        from terminal.question_tags import run_question_tags
        
        # Should complete without error even with no matches
        run_question_tags()
        
        assert mock_print.call_count > 0


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_filter_with_unicode_tags(self):
        """Test filtering with unicode characters in tags"""
        from terminal.question_tags import filter_by_tag
        
        questions = [
            {"question": "Q1", "tags": ["日本語", "한국어"], "correct_index": 0, "options": []},
            {"question": "Q2", "tags": ["中文", "Español"], "correct_index": 0, "options": []}
        ]
        
        result = filter_by_tag(questions, ["日本語"])
        
        assert len(result) == 1
        assert result[0]["question"] == "Q1"
    
    def test_filter_with_special_characters(self):
        """Test filtering with special characters in tags"""
        from terminal.question_tags import filter_by_tag
        
        questions = [
            {"question": "Q1", "tags": ["C++", "C#"], "correct_index": 0, "options": []},
            {"question": "Q2", "tags": ["Python 3.x"], "correct_index": 0, "options": []}
        ]
        
        result = filter_by_tag(questions, ["C++", "Python 3.x"])
        
        assert len(result) == 2
    
    def test_calculate_scores_with_out_of_range_answers(self):
        """Test scoring with invalid answer indices"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = [
            {"question": "Q1", "tags": ["Test"], "correct_index": 0, "options": ["A", "B"]}
        ]
        student_answers = [99]  # Out of range
        
        result = calculate_tag_scores(questions, student_answers)
        
        # Should still process (answer won't match correct_index)
        assert result["Test"]["correct"] == 0
        assert result["Test"]["total"] == 1
    
    def test_calculate_scores_with_negative_answers(self):
        """Test scoring with negative answer indices"""
        from terminal.question_tags import calculate_tag_scores
        
        questions = [
            {"question": "Q1", "tags": ["Test"], "correct_index": 0, "options": []}
        ]
        student_answers = [-1]
        
        result = calculate_tag_scores(questions, student_answers)
        
        assert result["Test"]["correct"] == 0
        assert result["Test"]["total"] == 1
    
    def test_long_tag_names(self):
        """Test with very long tag names"""
        from terminal.question_tags import filter_by_tag
        
        long_tag = "This is a very long tag name " * 10
        questions = [
            {"question": "Q1", "tags": [long_tag], "correct_index": 0, "options": []}
        ]
        
        result = filter_by_tag(questions, [long_tag])
        
        assert len(result) == 1
    
    def test_many_tags_per_question(self):
        """Test questions with many tags"""
        from terminal.question_tags import filter_by_tag, calculate_tag_scores
        
        many_tags = [f"Tag{i}" for i in range(50)]
        questions = [
            {"question": "Q1", "tags": many_tags, "correct_index": 0, "options": []}
        ]
        
        # Filter should work
        result = filter_by_tag(questions, [many_tags[0]])
        assert len(result) == 1
        
        # Scoring should work
        scores = calculate_tag_scores(questions, [0])
        assert len(scores) == 50  # All tags should be in scores


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_full_workflow_integration(self):
        """Test complete workflow from filtering to reporting"""
        from terminal.question_tags import filter_by_tag, calculate_tag_scores, generate_tag_report
        
        # Filter questions
        selected_tags = ["NLP", "Machine Learning"]
        filtered = filter_by_tag(SAMPLE_QUESTION_BANK, selected_tags)
        
        assert len(filtered) == 2
        
        # Simulate student answers
        student_answers = [0, 1]  # First correct, second wrong
        
        # Calculate scores
        scores = calculate_tag_scores(filtered, student_answers)
        
        assert scores["NLP"]["correct"] == 1
        assert scores["Machine Learning"]["correct"] == 0
        
        # Generate report
        with patch('builtins.print') as mock_print:
            generate_tag_report(scores)
            assert mock_print.call_count > 0
    
    def test_save_and_load_tag_template(self):
        """Test saving and loading tag template"""
        selected_tags = ["NLP", "Deep Learning"]
        template_data = {"selected_tags": selected_tags}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            # Save template
            with open(tmp_path, 'w') as f:
                json.dump(template_data, f, indent=4)
            
            # Load template
            with open(tmp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == template_data
            assert loaded["selected_tags"] == selected_tags
        finally:
            os.unlink(tmp_path)
    
    def test_multiple_quiz_sessions(self):
        """Test running multiple quiz sessions with different tags"""
        from terminal.question_tags import filter_by_tag, calculate_tag_scores
        
        # Session 1: NLP focus
        session1_questions = filter_by_tag(SAMPLE_QUESTION_BANK, ["NLP"])
        session1_answers = [0]
        session1_scores = calculate_tag_scores(session1_questions, session1_answers)
        
        # Session 2: ML focus
        session2_questions = filter_by_tag(SAMPLE_QUESTION_BANK, ["Machine Learning"])
        session2_answers = [0]
        session2_scores = calculate_tag_scores(session2_questions, session2_answers)
        
        # Both sessions should work independently
        assert "NLP" in session1_scores
        assert "Machine Learning" in session2_scores
        assert "Machine Learning" not in session1_scores
        assert "NLP" not in session2_scores


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])