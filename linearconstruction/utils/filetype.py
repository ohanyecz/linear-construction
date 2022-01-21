from gettext import gettext as _
from pathlib import Path
import sys

__all__ = ["FileType"]


class FileType:
    """
    Factory for creating file object types.

    Instances of *OutputFileType* are typically passed as type= arguments to the
    `~argparse.ArgumentParser.add_argument` method.

    This class is similar to `~argparse.FileType` but modified to create the output file.

    Attributes
    ----------
    mode: str
        A string indicating how the file is to be opened. Accepts the same values as the
        builtin `open()` function.
    bufsize: int
        The file's desired buffer size. Accepts the same values as the builtin `open()` function.
    encoding: str
        The file's encoding. Accepts the same values as the builtin `open()` function.
    errors: str
        A string indicating how encoding and decoding errors are to be handled.
        Accepts the same values as the builtin `open()` function.


    Raises
    ------
    ValueError
        If *mode* is invalid for *sys.stdout*.

    """
    def __init__(self, mode="r", bufsize=-1, encoding=None, errors=None):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        if string == "-":
            if "r" in self._mode:
                return sys.stdin
            elif "w" in self._mode:
                return sys.stdout
            else:
                msg = _(f"argument '-' with mode {self._mode}")
                raise ValueError(msg)

        # all other arguments are used as file names
        output_path = Path(string)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            msg = _(f"Created output file '{output_path}'")
            print(msg)
        return output_path.open(self._mode, self._bufsize, self._encoding, self._errors)
