import pytest
from terminal.difficulty import generate_quiz

class TestUserStory13:

    def test_generate_quiz_easy_only_returns_easy_questions(self):
        quiz = generate_quiz("easy", num_questions=2)
        assert len(quiz) <= 2
        for q in quiz:
            assert q["difficulty"] == "easy"

    def test_generate_quiz_medium_only_returns_medium_questions(self):
        quiz = generate_quiz("medium", num_questions=2)
        assert len(quiz) <= 2
        for q in quiz:
            assert q["difficulty"] == "medium"

    def test_generate_quiz_invalid_difficulty_raises_error(self):
        with pytest.raises(ValueError):
            generate_quiz("unknown-level")
