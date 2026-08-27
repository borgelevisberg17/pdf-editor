"""Operações de PDF orientadas a fluxos web.

O módulo mantém as operações de arquivo isoladas da camada Flask para que os
mesmos recursos possam ser reutilizados por CLI, testes e futuras APIs.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter


class PdfOperationError(ValueError):
    """Erro de validação amigável para operações com páginas de PDF."""


def parse_page_spec(spec: str | None, total_pages: int) -> list[int]:
    """Converte uma especificação como ``1,3-5`` em índices zero-based."""
    if total_pages < 1:
        raise PdfOperationError("O PDF não contém páginas legíveis.")

    value = (spec or "all").strip().lower()
    if value in {"", "all", "todas", "todos"}:
        return list(range(total_pages))

    selected: set[int] = set()
    for token in re.split(r"[,;\s]+", value):
        if not token:
            continue
        if token in {"odd", "ímpares", "impares"}:
            selected.update(range(0, total_pages, 2))
            continue
        if token in {"even", "pares"}:
            selected.update(range(1, total_pages, 2))
            continue

        if "-" in token:
            start_raw, end_raw = token.split("-", 1)
            try:
                start, end = int(start_raw), int(end_raw)
            except ValueError as exc:
                raise PdfOperationError(f"Intervalo inválido: {token}") from exc
            if start > end:
                start, end = end, start
            numbers = range(start, end + 1)
        else:
            try:
                numbers = [int(token)]
            except ValueError as exc:
                raise PdfOperationError(f"Página inválida: {token}") from exc

        for number in numbers:
            if number < 1 or number > total_pages:
                raise PdfOperationError(
                    f"A página {number} não existe. O PDF possui {total_pages} página(s)."
                )
            selected.add(number - 1)

    result = sorted(selected)
    if not result:
        raise PdfOperationError("Selecione pelo menos uma página.")
    return result


def _new_writer() -> PdfWriter:
    writer = PdfWriter()
    writer.add_metadata({"/Producer": "BorgePDF"})
    return writer


def merge_pdfs(input_paths: Iterable[str | Path], output_path: str | Path) -> int:
    writer = _new_writer()
    count = 0
    for path in input_paths:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
            count += 1
    if count == 0:
        raise PdfOperationError("Nenhuma página foi encontrada para mesclar.")
    with open(output_path, "wb") as output:
        writer.write(output)
    return count


def compress_pdf(input_path: str | Path, output_path: str | Path) -> int:
    """Reescreve o PDF compactando streams de conteúdo quando possível."""
    reader = PdfReader(str(input_path))
    writer = _new_writer()
    for page in reader.pages:
        try:
            page.compress_content_streams()
        except Exception:
            pass
        writer.add_page(page)
    if not reader.pages:
        raise PdfOperationError("O PDF não contém páginas legíveis.")
    with open(output_path, "wb") as output:
        writer.write(output)
    return len(reader.pages)


def split_pdf(input_path: str | Path, output_path: str | Path, page_spec: str) -> int:
    reader = PdfReader(str(input_path))
    pages = parse_page_spec(page_spec, len(reader.pages))
    writer = _new_writer()
    for index in pages:
        writer.add_page(reader.pages[index])
    with open(output_path, "wb") as output:
        writer.write(output)
    return len(pages)


def rotate_pdf(input_path: str | Path, output_path: str | Path, angle: int, page_spec: str) -> int:
    if angle not in {90, 180, 270}:
        raise PdfOperationError("A rotação deve ser 90, 180 ou 270 graus.")
    reader = PdfReader(str(input_path))
    selected = set(parse_page_spec(page_spec, len(reader.pages)))
    writer = _new_writer()
    for index, page in enumerate(reader.pages):
        if index in selected:
            page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as output:
        writer.write(output)
    return len(selected)


def delete_pages(input_path: str | Path, output_path: str | Path, page_spec: str) -> int:
    reader = PdfReader(str(input_path))
    remove = set(parse_page_spec(page_spec, len(reader.pages)))
    remaining = [index for index in range(len(reader.pages)) if index not in remove]
    if not remaining:
        raise PdfOperationError("A operação removeria todas as páginas do PDF.")
    writer = _new_writer()
    for index in remaining:
        writer.add_page(reader.pages[index])
    with open(output_path, "wb") as output:
        writer.write(output)
    return len(remove)


def reorder_pages(input_path: str | Path, output_path: str | Path, order_spec: str) -> int:
    reader = PdfReader(str(input_path))
    order = parse_page_spec(order_spec, len(reader.pages))
    if len(order) != len(reader.pages) or set(order) != set(range(len(reader.pages))):
        raise PdfOperationError("A nova ordem deve conter todas as páginas exatamente uma vez.")
    writer = _new_writer()
    for index in order:
        writer.add_page(reader.pages[index])
    with open(output_path, "wb") as output:
        writer.write(output)
    return len(order)


def pdf_info(input_path: str | Path) -> dict[str, int | str]:
    reader = PdfReader(str(input_path))
    return {
        "pages": len(reader.pages),
        "title": str(reader.metadata.title or "") if reader.metadata else "",
        "size": Path(input_path).stat().st_size,
    }
