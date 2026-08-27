from io import BytesIO
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pypdf import PdfReader, PdfWriter


def make_pdf(path: Path, pages: int = 3) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=400)
    with path.open("wb") as file:
        writer.write(file)


def main() -> None:
    from app import app, init_db
    from modules.pdf_operations import (
        delete_pages,
        merge_pdfs,
        parse_page_spec,
        reorder_pages,
        rotate_pdf,
        split_pdf,
    )

    assert parse_page_spec("1,3-4", 4) == [0, 2, 3]
    assert parse_page_spec("odd", 4) == [0, 2]

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source.pdf"
        second = root / "second.pdf"
        merged = root / "merged.pdf"
        split = root / "split.pdf"
        rotated = root / "rotated.pdf"
        deleted = root / "deleted.pdf"
        reordered = root / "reordered.pdf"
        make_pdf(source)
        make_pdf(second, 1)
        assert merge_pdfs([source, second], merged) == 4
        assert split_pdf(source, split, "1,3") == 2
        assert rotate_pdf(source, rotated, 90, "all") == 3
        assert delete_pages(source, deleted, "2") == 1
        assert reorder_pages(source, reordered, "3,1,2") == 3
        assert len(PdfReader(str(merged)).pages) == 4
        assert len(PdfReader(str(split)).pages) == 2
        assert len(PdfReader(str(deleted)).pages) == 2

    init_db()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Seu PDF" in response.data
    assert b"Comprimir PDF" in response.data

    pdf_bytes = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=400)
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    upload_response = client.post(
        "/compress-pdf",
        data={"pdf_file": (pdf_bytes, "sample.pdf"), "output_name": "compactado.pdf"},
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 200
    assert upload_response.headers.get("Content-Type") == "application/pdf"

    txt_response = client.post(
        "/txt-to-pdf",
        data={"txt_files": (BytesIO(b"# Relatorio\\n\\nConteudo de teste."), "notes.md")},
        content_type="multipart/form-data",
    )
    assert txt_response.status_code == 200
    assert txt_response.headers.get("Content-Type") == "application/pdf"
    print("smoke_app: ok")


if __name__ == "__main__":
    main()
