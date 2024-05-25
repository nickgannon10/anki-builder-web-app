import requests
from bs4 import BeautifulSoup
import tiktoken
from typing import List

class WebPagePreprocessor:
    def __init__(self, url: str):
        """
        Initializes the WebPagePreprocessor with the given URL.

        :param url: URL of the web page to preprocess.
        """
        self.url = url
        self.html_content: str = ""
        self.text_content: str = ""
        self.chunks: List[str] = []
        self.total_tokens: int = 0

    def fetch_content(self) -> None:
        """
        Fetches the HTML content from the web page.
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            self.html_content = response.text
        else:
            raise Exception(f"Failed to fetch web page. Status code: {response.status_code}")

    def extract_text(self) -> None:
        """
        Extracts text content from the HTML content of the web page.
        """
        if not self.html_content:
            raise Exception("HTML content is empty. Fetch content first.")
        
        soup = BeautifulSoup(self.html_content, 'html.parser')
        
        paragraphs = soup.find_all('p')
        self.text_content = "\n".join([para.get_text() for para in paragraphs])

    def chunk_text(self, max_tokens: int = 1500) -> None:
        """
        Chunks the text content into increments of specified maximum tokens.

        :param max_tokens: Maximum number of tokens per chunk.
        """
        if not self.text_content:
            raise Exception("Text content is empty. Extract text first.")
        
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(self.text_content)
        self.total_tokens = len(tokens)  # Counting total tokens
        
        self.chunks = [tokenizer.decode(tokens[i:i + max_tokens]) for i in range(0, len(tokens), max_tokens)]

    def get_chunks(self) -> List[str]:
        """
        Returns the chunks.

        :return: List of chunks.
        """
        return self.chunks