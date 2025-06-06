from typing import List


def clarification_context(clarification_questions: List[str], clarification_answers: List[str]) -> str:
    """
    Generate a clarification context based on the clarification questions and answers
    """
    clarification_context = ""
    for question, answer in zip(clarification_questions, clarification_answers):
        clarification_context += f"Question: {question}\nAnswer: {answer}\n"
    return clarification_context