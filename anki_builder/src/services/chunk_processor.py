import logging
import json
import os
from typing import List, Dict
from src.utils.openai_client import OpenAIClient

class ChunkProcessor:
    def __init__(self, chunks: List[str]):
        """
        Initializes the ChunkProcessor with the given chunk data.

        :param chunks: List of chunks.
        """
        self.chunks = chunks
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """
        Loads the prompt template from the markdown file.

        :return: Prompt template as a string.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, '..', 'prompts', 'chunk_to_notecard.md')

        with open(prompt_path, "r") as file:
            prompt_template = file.read()
        return prompt_template

    def process_chunks(self, num_chunks: int = 1) -> List[Dict]:
        """
        Processes the specified number of chunks using the OpenAI client.

        :param num_chunks: Number of chunks to process.
        :return: List of flashcards with front and back content.
        """
        if not self.chunks:
            logging.info("No chunks found.")
            return []

        openai_client = OpenAIClient()
        flashcards = []

        for i, chunk in enumerate(self.chunks[:num_chunks]):
            prompt = self.prompt_template.replace("{TEXT_CONTENT}", chunk)
            messages = [{"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                        {"role": "user", "content": prompt}]
            response = openai_client.generate_completion(messages=messages)
            
            if response.choices[0].finish_reason == "stop":
                try:
                    json_response = json.loads(response.choices[0].message.content)
                    # Extract flashcards from the JSON response
                    if "flashcards" in json_response:
                        flashcards.extend(json_response["flashcards"])
                    else:
                        logging.error("No flashcards key in the JSON response")
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}")
                    flashcards.append({"error": "Failed to parse JSON response"})
            else:
                flashcards.append({"error": "Response not completed successfully"})

            logging.info(f"Chunk {i+1} response: {response}")

        return flashcards