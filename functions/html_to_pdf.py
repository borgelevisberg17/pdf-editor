from weasyprint import HTML

def html_para_pdf(html_path, output_path):
    """
    Converts an HTML file to a PDF file.

    Args:
        html_path (str): The path to the input HTML file.
        output_path (str): The path to save the output PDF file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        HTML(html_path).write_pdf(output_path)
        return True
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        return False
