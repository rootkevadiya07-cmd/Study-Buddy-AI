import fitz  # PyMuPDF
import re
from typing import Dict, Any

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted PDF text."""
    if not text:
        return ""
    # Replace multiple newlines with standard spacing
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def process_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
    """
    Process PDF bytes and extract text and metadata.
    
    Returns a dictionary with:
        - success: bool
        - filename: str
        - page_count: int
        - char_count: int
        - text: str
        - pages: list of str (page-by-page text)
        - error: str (if failed)
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if doc.page_count == 0:
            return {
                "success": False,
                "filename": filename,
                "error": "The uploaded PDF document contains no pages."
            }
            
        pages = []
        total_text = []
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text") or ""
            cleaned_page = clean_extracted_text(page_text)
            pages.append(cleaned_page)
            if cleaned_page:
                total_text.append(f"--- Page {page_num + 1} ---\n{cleaned_page}")
                
        full_text = "\n\n".join(total_text).strip()
        
        if not full_text or len(full_text) < 10:
            return {
                "success": False,
                "filename": filename,
                "error": "Could not extract readable text from the PDF. It may contain scanned images or be empty. Please upload a PDF with selectably readable text."
            }
            
        return {
            "success": True,
            "filename": filename,
            "page_count": doc.page_count,
            "char_count": len(full_text),
            "text": full_text,
            "pages": pages,
            "error": None
        }

    except fitz.FileDataError:
        return {
            "success": False,
            "filename": filename,
            "error": "Invalid or corrupted PDF file. Please verify the file and try again."
        }
    except Exception as e:
        return {
            "success": False,
            "filename": filename,
            "error": f"Failed to process PDF file: {str(e)}"
        }
