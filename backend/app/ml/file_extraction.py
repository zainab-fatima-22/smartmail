"""
file_extraction.py
--------------------
Extracts plain text from an uploaded email file (.txt or .eml).

WHAT are we doing?
    - .txt files: decode the raw bytes as UTF-8 text directly.
    - .eml files: parse them as a real email message (using Python's
      built-in `email` module) and pull out the plain-text body, since
      .eml files include headers (From, To, Subject...) and sometimes
      HTML/multipart content we don't want to feed straight into the
      classifier.

WHY not just decode .eml as raw text?
    An .eml file's headers ("From: ...", "Content-Type: ...") would
    confuse the classifier — it would be reading email PLUMBING, not
    email CONTENT. Parsing it properly extracts just the message body,
    which is what the model was trained to classify.

WHICH file:
    backend/app/ml/file_extraction.py

HOW it connects to other files:
    - Used by api/routes/upload.py.
"""

from email import policy
from email.parser import BytesParser


class FileExtractionError(ValueError):
    """Raised when a file's text cannot be extracted (corrupt, empty, unreadable)."""


def extract_text_from_txt(raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to latin-1, which never raises, rather than reject
        # a file just because it wasn't strictly UTF-8.
        return raw_bytes.decode("latin-1")


def extract_text_from_eml(raw_bytes: bytes) -> str:
    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    except Exception as e:
        raise FileExtractionError(f"Could not parse .eml file: {e}")

    body_part = message.get_body(preferencelist=("plain", "html"))
    if body_part is None:
        raise FileExtractionError("No readable message body found in this .eml file.")

    content = body_part.get_content()
    if body_part.get_content_type() == "text/html":
        # Very small, dependency-free HTML tag stripper — good enough for
        # simple .eml bodies. Not a full HTML parser, but this project
        # deliberately avoids adding heavy dependencies for a Day 4 extra.
        import re

        content = re.sub(r"<[^>]+>", " ", content)

    return content


def extract_text_from_upload(filename: str, raw_bytes: bytes) -> str:
    """Dispatch to the right extractor based on file extension."""
    lower_name = filename.lower()
    if lower_name.endswith(".txt"):
        text = extract_text_from_txt(raw_bytes)
    elif lower_name.endswith(".eml"):
        text = extract_text_from_eml(raw_bytes)
    else:
        raise FileExtractionError(f"Unsupported file type: {filename}")

    if not text.strip():
        raise FileExtractionError("The uploaded file is empty.")

    return text
