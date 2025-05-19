import os
import pytest
from anki_builder.src.services.pdf_processor import PDFPreprocessor


def test_pdf_processor_extract_and_chunk():
    pytest.importorskip("fitz")
    pytest.importorskip("tiktoken")

    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "anki_builder", "pdfs", "SelfRAG.pdf"))
    preprocessor = PDFPreprocessor(pdf_path)
    preprocessor.extract_text()
    preprocessor.chunk_text(max_tokens=100)

    assert preprocessor.text_content
    assert preprocessor.chunks
    assert preprocessor.total_tokens > 0
