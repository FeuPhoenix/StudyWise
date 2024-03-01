from ast import List


class Questions_Repo:
    def __init__(self, text: str, options: List[str], correct_answer: str):
        self.text = text  # The text of the question
        self.options = options  # A list of answer options
        self.correct_answer = correct_answer  # The index of the correct option in the options list

    def check_answer(self, correct_answer: str) -> bool:
        """Check if the user's selected option index is correct."""
        return correct_answer == self.correct_answer

    def get_correct_answer(self) -> str:
        """Get the correct answer text."""
        return self.options[self.correct_answer]

    
