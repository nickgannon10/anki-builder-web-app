# Goal

Generate flashcards based on the provided text content.

## Instructions

You are given a chunk of text from a document. Your task is to generate flashcards that will help someone study the content effectively. Each flashcard should have a question (front) and an answer (back).

## Additional Context

The document may contain various types of information, including definitions, explanations, and examples. Focus on extracting key points, important details, and useful information that can be turned into question-answer pairs.

## Text Content

{TEXT_CONTENT}

## Output Format

Please format your output as a JSON list of flashcards, with each flashcard containing a "front" and a "back".

Example:
[
{
"front": "What is the capital of France?",
"back": "Paris"
},
{
"front": "Explain the concept of natural selection.",
"back": "Natural selection is the process by which species adapt to their environment as individuals with favorable traits survive and reproduce."
}
]
