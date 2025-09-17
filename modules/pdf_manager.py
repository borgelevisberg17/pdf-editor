from pypdf import PdfReader, PdfWriter

def mesclar_pdfs(pdf_paths, output_path):
    """
    Merges multiple PDF files into a single PDF file.

    Args:
        pdf_paths (list): A list of paths to the PDF files to merge.
        output_path (str): The path to save the merged PDF file.

    Returns:
        bool: True if the merge was successful, False otherwise.
    """
    pdf_writer = PdfWriter()
    try:
        for path in pdf_paths:
            pdf_reader = PdfReader(path)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        with open(output_path, "wb") as out:
            pdf_writer.write(out)
        return True
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False
