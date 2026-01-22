"""Python implementation of ASCII85/ASCIIHex decoder (Adobe version)."""

import re
from base64 import a85decode
from binascii import unhexlify

_WHITESPACE = b" \t\n\r\f\v"

start_re = re.compile(rb"^\s*<?\s*~\s*")
end_re = re.compile(rb"\s*~\s*>?\s*$")


def ascii85decode(data: bytes) -> bytes:
    """In ASCII85 encoding, every four bytes are encoded with five ASCII
    letters, using 85 different types of characters (as 256**4 < 85**5).
    When the length of the original bytes is not a multiple of 4, a special
    rule is used for round up.

    Adobe's ASCII85 implementation expects the input to be terminated
    by `b"~>"`, and (though this is absent from the PDF spec) it can
    also begin with `b"<~"`.  We can't reliably expect this to be the
    case, and there can be off-by-one errors in stream lengths which
    mean we only see `~` at the end.  Worse yet, `<` and `>` are
    ASCII85 digits, so we can't strip them.  We settle on a compromise
    where we strip leading `<~` or `~` and trailing `~` or `~>`.
    """
    n = len(data)

    # Trim start: match r"^\s*<?\s*~\s*"
    i = 0
    while i < n and data[i] in _WHITESPACE:
        i += 1
    if i < n and data[i] == 0x3C:  # ord('<')
        i += 1
        while i < n and data[i] in _WHITESPACE:
            i += 1
    if i < n and data[i] == 0x7E:  # ord('~')
        i += 1
        while i < n and data[i] in _WHITESPACE:
            i += 1
        start_idx = i
    else:
        start_idx = 0

    # Trim end: match r"\s*~\s*>?\s*$"
    j = n
    while j > 0 and data[j - 1] in _WHITESPACE:
        j -= 1
    pos = j
    if pos > 0 and data[pos - 1] == 0x3E:  # ord('>')
        pos -= 1
    while pos > 0 and data[pos - 1] in _WHITESPACE:
        pos -= 1
    if pos > 0 and data[pos - 1] == 0x7E:  # ord('~')
        k = pos - 1
        while k > 0 and data[k - 1] in _WHITESPACE:
            k -= 1
        end_idx = k
    else:
        end_idx = n

    return a85decode(data[start_idx:end_idx])


bws_re = re.compile(rb"\s")


def asciihexdecode(data: bytes) -> bytes:
    """ASCIIHexDecode filter: PDFReference v1.4 section 3.3.1
    For each pair of ASCII hexadecimal digits (0-9 and A-F or a-f), the
    ASCIIHexDecode filter produces one byte of binary data. All white-space
    characters are ignored. A right angle bracket character (>) indicates
    EOD. Any other characters will cause an error. If the filter encounters
    the EOD marker after reading an odd number of hexadecimal digits, it
    will behave as if a 0 followed the last digit.
    """
    data = bws_re.sub(b"", data)
    idx = data.find(b">")
    if idx != -1:
        data = data[:idx]
        if idx % 2 == 1:
            data += b"0"
    return unhexlify(data)
