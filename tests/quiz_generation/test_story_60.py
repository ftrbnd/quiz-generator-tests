from terminal.shuffle import shuffle_answers

def test_shuffle_answers_preserves_correct_answer():
    question = {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    }

    shuffled = shuffle_answers(question)

    # Correct answer MUST still be present
    assert "4" in shuffled["options"], "Correct answer missing after shuffle"

def test_shuffle_answers_does_not_mutate_original():
    original = {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    }

    shuffled = shuffle_answers(original)

    # Original should remain unchanged
    assert original["options"] == ["3", "4", "5", "6"], "Original question was modified"

def test_shuffle_answers_changes_order_most_of_the_time():
    # There is a small chance order may match by luck, so we repeat.
    question = {
        "question": "Test shuffle",
        "options": ["A", "B", "C", "D"],
        "answer": "A"
    }

    orders = set()
    for _ in range(10):
        shuffled = shuffle_answers(question)
        orders.add(tuple(shuffled["options"]))

    # More than one unique ordering means shuffling is happening
    assert len(orders) > 1, "Options are not being shuffled"

