import os
import argparse
from pdf2image import convert_from_path
import pytesseract
import re
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# Set Tesseract path explicitly
pytesseract.pytesseract.tesseract_cmd = r'{PATH_TO_TESSERACT_EXE}'

# Temporarily add Poppler path
os.environ["PATH"] += os.pathsep + r'{PATH_TO_POPPLER_BINARIES}'

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def ocr_pdf_to_text(pdf_path):
    try:
        print(f"Performing OCR on {pdf_path}...")
        images = convert_from_path(pdf_path)
        text = pytesseract.image_to_string(images[0])
        print("OCR completed successfully.")
        print(f"Extracted text: {text[:1000]}")  # Print first 1000 characters of the extracted text
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None

def extract_info_from_text(text):
    try:
        print("Extracting information from text...")
        facture_pattern = r"FACTURE\s*#?\s*(\d+)"
        company_pattern = r"VIA BOIS INC"
        date_pattern = r"(\d{4}/\d{2}/\d{2})"

        facture_match = re.search(facture_pattern, text, re.IGNORECASE)
        company_match = re.search(company_pattern, text, re.IGNORECASE)
        date_match = re.search(date_pattern, text, re.IGNORECASE)

        if facture_match:
            print(f"Facture match: {facture_match.group(0)}")
        if company_match:
            print(f"Company match: {company_match.group(0)}")
        if date_match:
            print(f"Date match: {date_match.group(0)}")

        # Collecting the parts for the filename
        parts = []
        if facture_match:
            number = facture_match.group(1)
            parts.append(f"FAC_{number}")
        if company_match:
            company_name = company_match.group(0).replace(" ", "")
            parts.append(company_name)
        if date_match:
            date_str = date_match.group(1)
            date_obj = datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            parts.append(date_obj)

        if parts:
            new_filename = "_".join(parts)
            print("Information extraction successful.")
            return new_filename
        else:
            print("Failed to extract required information.")
            return None
    except Exception as e:
        print(f"Error during information extraction: {e}")
        return None

def rename_pdf(pdf_path):
    try:
        text = ocr_pdf_to_text(pdf_path)
        if text is None:
            print("Failed to perform OCR on the PDF.")
            return
        
        new_filename = extract_info_from_text(text)
        if not new_filename:
            print("Failed to generate a valid filename.")
            return

        new_filename += ".pdf"
        dir_path = os.path.dirname(pdf_path)
        new_file_path = os.path.join(dir_path, new_filename)
        
        os.rename(pdf_path, new_file_path)
        print(f"File renamed to: {new_file_path}")
    except Exception as e:
        print(f"Error during renaming: {e}")

def main():
    parser = argparse.ArgumentParser(description="PDF File Renamer using OCR")
    parser.add_argument("pdf_path", help="Path to the PDF file to rename")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_path):
        print("Error: The specified file does not exist.")
        return

    rename_pdf(args.pdf_path)

if __name__ == "__main__":
    try:
        print(f"Checking for files in: {DOWNLOADS_DIR}")
        
        if not os.path.exists(DOWNLOADS_DIR):
            print("Downloads directory does not exist.")
        else:
            all_files = os.listdir(DOWNLOADS_DIR)
            print(f"All files in the Downloads directory: {all_files}")

            # Use lower() to handle case insensitivity
            pdf_files = [f for f in all_files if f.lower().endswith(".pdf")]
            print(f"Found PDF files: {pdf_files}")

            if not pdf_files:
                print("No PDF files found in the Downloads directory.")
            else:
                pdf_completer = WordCompleter(pdf_files, ignore_case=True)
                pdf_filename = prompt("Select a PDF file: ", completer=pdf_completer)
                
                pdf_path = os.path.join(DOWNLOADS_DIR, pdf_filename)

                # Simulate passing the argument to argparse
                import sys
                sys.argv.append(pdf_path)
                
                main()
    except Exception as e:
        print(f"Error during execution: {e}")