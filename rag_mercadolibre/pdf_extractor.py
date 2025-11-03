import pdfplumber
import re

def extract_tracking_number_from_pdf(pdf_path):
    """
    Extracts text from a PDF and searches for a tracking number pattern.
    A common Servientrega tracking number is a string of 10 or more digits.
    """
    tracking_numbers = []
    # Pattern for 10 or more digits (common for logistics tracking numbers)
    # You might need to adjust this pattern for higher accuracy.
    tracking_pattern = r'\b\d{10,20}\b' 
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # We will process a sample of the first three pages
            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text:
                    # Find all matches of the pattern in the text
                    matches = re.findall(tracking_pattern, text)
                    # Add unique matches to our list
                    for number in matches:
                        if number not in tracking_numbers:
                            tracking_numbers.append(number)
                            
        if tracking_numbers:
            # Simple RAG-like grounding: the extracted numbers
            print(f"RAG-like Extraction Success: Found {len(tracking_numbers)} potential tracking numbers.")
            return tracking_numbers
        else:
            print("Extraction Failure: No suitable number found.")
            return []

    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
        return []

# Example Usage (assuming you have a file named 'invoice.pdf')
# tracking_list = extract_tracking_number_from_pdf('path/to/your/invoice.pdf')
# print(tracking_list)