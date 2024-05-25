import fitz  # PyMuPDF
import tiktoken
from typing import List

class PDFPreprocessor:
    def __init__(self, pdf_path: str):
        """
        Initializes the PDFPreprocessor with the given PDF file path.

        :param pdf_path: Path to the PDF file to preprocess.
        """
        self.pdf_path = pdf_path
        self.text_content: str = ""
        self.chunks: List[str] = []
        self.total_tokens: int = 0

    def extract_text(self) -> None:
        """
        Extracts text content from the PDF file.
        """
        doc = fitz.open(self.pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        self.text_content = text

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