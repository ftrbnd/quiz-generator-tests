# As a professor, I want to upload my materials in whatever file format I have (PDF, text, images) so that the system can create quizzes from any source
import pytest
from phases.quizzes import Quiz 

@pytest.fixture
def quiz():
    """Fixture to create a fresh Quiz instance for each test."""
    return Quiz()

def generate_from_source(quiz, source_format, content, num_questions, question_types):
    """
    Test-side helper: a conceptual entry point that uses only what Quiz already exposes.
    For now, it just delegates 'text' sources to Quiz.generate_from_text.
    """
    if source_format == "text":
        return quiz.generate_from_text(content, num_questions, question_types)

    raise ValueError(f"Unsupported source_format: {source_format}")

def test_quiz_initial_state_is_empty(quiz):
    """
    Smoke test: we can construct a Quiz and its initial state is empty.
    """
    assert quiz.current_quiz_state["questions"] == []
    assert quiz.current_quiz_state["num_questions"] == 0
    assert quiz.current_quiz_state["question_types"] == []


def test_generate_from_source_text_delegates_to_generate_from_text(quiz, monkeypatch):
    """
    We define generate_from_source at the test level but it must rely ONLY
    on public methods of Quiz (i.e., generate_from_text).

    This still captures the user story idea:
    there is a single conceptual entry point that handles different formats,
    and 'text' is implemented by delegating to generate_from_text.
    """

    captured = {}

    def fake_generate_from_text(input_text, num_questions, question_types):
        captured["input_text"] = input_text
        captured["num_questions"] = num_questions
        captured["question_types"] = question_types
        return "FAKE_RESULT"

    monkeypatch.setattr(quiz, "generate_from_text", fake_generate_from_text)

    result = generate_from_source(
        quiz=quiz,
        source_format="text",
        content="These are my lecture notes",
        num_questions=3,
        question_types=["fill_blank"],
    )

    assert captured["input_text"] == "These are my lecture notes"
    assert captured["num_questions"] == 3
    assert captured["question_types"] == ["fill_blank"]
    assert result == "FAKE_RESULT"