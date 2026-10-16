BOOK_EXTENSIONS = {
    ".pdf",
    ".fb2",
    ".epub",
    ".zip",
    ".mobi",
    ".azw",
    ".azw3",
    ".azw4",
    ".kfx",
    ".kpf",
    ".djvu",
    ".djv",
    ".lit",
    ".prc",
    ".pdb",
    ".chm",
    ".cbz",
    ".cbr",
    ".rtf",
    ".txt",
}


def is_book_file(filename: str) -> bool:
    return any(
        filename.lower().endswith(ext)
        for ext in BOOK_EXTENSIONS
    )