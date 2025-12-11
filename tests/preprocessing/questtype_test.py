# As an instructor, I want to be able to specify the question types so that students demonstrate their knowledge in different ways
import pytest
from unittest.mock import patch
import gradio as gr
from phases.quizzes import Quiz 

@pytest.fixture
def quiz():
    """Return a fresh Quiz instance for each test."""
    return Quiz()

def test_quiz_initial_state(quiz):
    assert quiz.current_quiz_state == {
        "questions": [],
        "num_questions": 0,
        "question_types": []
    }

def set_question_types(self, question_types):
    """
    Store the instructor's chosen question types in the quiz state.
    For now, we just save them as-is.
    """
    self.current_quiz_state["question_types"] = list(question_types)

def test_generate_from_text_sets_question_types_in_state():
    """
    Calling generate_from_text with question_types should update
    the quiz's internal state so that question_types is recorded.
    """
    quiz = Quiz()

    input_text = "Photosynthesis is the process by which plants convert light energy into chemical energy."
    question_types = ["multiple_choice", "short_answer", "fill_blank"]

    quiz.generate("text", input_text, num_questions=3, question_types=question_types)

    assert quiz.current_quiz_state["question_types"] == question_types

def test_shuffle_does_not_change_question_types():
    """
    After generating a quiz with certain question types,
    shuffling should not change which question types are recorded.
    """
    quiz = Quiz()

    input_text = "The mitochondria is the powerhouse of the cell."
    question_types = ["fill_blank"] 

    quiz.generate("text", 
        input=input_text,
        num_questions=3,
        question_types=question_types,
    )

    before = list(quiz.current_quiz_state["question_types"])

    quiz.shuffle()

    assert quiz.current_quiz_state["question_types"] == before

def test_generate_from_text_overwrites_previous_question_types():
    """
    When generate_from_text is called multiple times with different
    question_types, the quiz should reflect the latest choice.
    """
    quiz = Quiz()

    
    quiz.generate("text", 
        input="First topic text",
        num_questions=2,
        question_types=["multiple_choice"],
    )
    first_types = list(quiz.current_quiz_state["question_types"])

    
    quiz.generate("text", 
        input="Second topic text",
        num_questions=2,
        question_types=["short_answer"],
    )
    second_types = list(quiz.current_quiz_state["question_types"])
    quiz.generate("text", 
        input="Third topic text",
        num_questions=2,
        question_types=["fill_blank"],
    )
    third_types = list(quiz.current_quiz_state["question_types"])

    assert first_types == ["multiple_choice"]
    assert second_types == ["short_answer"]
    assert third_types == ['fill_blank']
