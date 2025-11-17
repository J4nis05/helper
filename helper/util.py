import os
import time
import random
import operator
from collections import OrderedDict
from functools import reduce
from typing import Any, Dict, List, Mapping, Optional, Sequence

import pyperclip
from rich.table import Table
from urllib.parse import quote


class Util:
    """Miscellanious Utility Functions"""

    @staticmethod
    def randarr(array : list, forbidden = None):
        """Select a Random Element from an Array (List) and set an optional forbidden element

        Args:
            array (list): The List from which the Element should be chosen from
            forbidden (Any, optional): The Element that should not be Returned. Defaults to None.

        Returns:
            Any: The Selected Element
        """

        assert type(array) == list, "[Util.randarr()] Input Array must be a List"

        if forbidden == None: return random.choice(array)
        while True:
            selected = random.choice(array)
            if selected != forbidden: return selected


    @staticmethod
    def clear() -> None: 
        """Clears the Terminal (OS Independent)"""
        
        assert True != False, "[Util.clear()] Something is very wrong with your System"

        if os.name == "nt": os.system("cls")
        else: os.system("clear")


    @staticmethod
    def lorem(paragraphs: int = 1, sentences: int = 3, words: int = 10, start: bool = True) -> str:
        """Generate Filler Text

        Args:
            paragraphs (int): The Amount of Paragraphs to Generate. Defaults to 1
            sentences (int): The Amount of Sentences per paragraphs. Defaults to 3
            words (int): The Amount of Words per Sentence +/- 3. Defaults to 10
            start (bool): Should the Text start with the normal "Lorem ipsum dolor...". Defaults to True

        Returns:
            str: Generated Lorem Ipsum text
        """

        assert type(paragraphs) == int, "[Util.lorem()] Paragraph Count must be an Integer"
        assert type(sentences) == int, "[Util.lorem()] Sentence Count must be an Integer"
        assert type(words) == int, "[Util.lorem()] Word Count must be an Integer"
        assert type(start) == bool, "[Util.lorem()] Start must be a bool"

        def _generate_sentence(length: int):
            sentence_array = []
            length = random.randint((length - 3), (length + 3))

            while len(sentence_array) < length:
                sentence_array.append(random.choice(vocabulary))

            sentence = ' '.join(sentence_array) + "."
            return sentence.capitalize()

        content = []
        first_sentence = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        vocabulary = [
            "a", "ac", "accumsan", "ad", "adipiscing", "aenean", "aliquam", "aliquet", "amet", "ante", "aptent", "arcu", "at", "auctor", 
            "bibendum", "blandit", 
            "class", "commodo", "condimentum", "congue", "consectetur", "consequat", "conubia", "convallis", "cras", "cubilia", "cum", "curabitur", "curae", 
            "dapibus", "diam", "dictum", "dictumst", "dignissim", "dolor", "donec", "dui", "duis", 
            "egestas", "eget", "eleifend", "elementum", "elit", "enim", "erat", "eros", "est", "et", "etiam", "eu", "euismod", 
            "facilisi", "faucibus", "felis", "fermentum", "feugiat", "fringilla", "fusce", 
            "gravida", 
            "habitant", "habitasse", "hac", "hendrerit", "himenaeos", 
            "iaculis", "id", "imperdiet", "in", "inceptos", "integer", "interdum", "ipsum", 
            "justo", 
            "lacinia", "lacus", "laoreet", "lectus", "leo", "ligula", "litora", "lobortis", "lorem", "luctus", 
            "maecenas", "magna", "magnis", "malesuada", "massa", "mattis", "mauris", "metus", "mi", "molestie", "mollis", "montes", "morbi", "mus", 
            "nam", "nascetur", "natoque", "nec", "neque", "netus", "nisi", "nisl", "non", "nostra", "nulla", "nullam", "nunc",
            "odio", "orci", "ornare", 
            "parturient", "pellentesque", "penatibus", "per", "pharetra", "phasellus", "placerat", "platea", "porta", "porttitor", "posuere", "potenti", "praesent", "pretium", "primis", "proin", "pulvinar", "purus", 
            "quam", "quis", "quisque", 
            "rhoncus", "ridiculus", "risus", "rutrum", 
            "sagittis", "sapien", "scelerisque", "sed", "sem", "semper", "senectus", "sit", "sociis", "sociosqu", "sodales", "sollicitudin", "suscipit", "suspendisse", 
            "taciti", "tellus", "tempor", "tempus", "tincidunt", "torquent", "tortor", "turpis", 
            "ullamcorper", "ultrices", "ultricies", "urna", 
            "varius", "vehicula", "vel", "velit", "venenatis", "vestibulum", "vitae", "vivamus", "viverra", "volutpat", "vulputate"
        ]

        for i in range(0, paragraphs):
            current_paragraph = []

            if i == 0 and start: current_paragraph.append(first_sentence)

            for j in range(0, sentences):
                current_sentence = _generate_sentence(words)
                current_paragraph.append(current_sentence)

            content.append(" ".join(current_paragraph))

        return "\n\n".join(content)


    @staticmethod
    def win95() -> str:
        """Generate a (semi) reliable Windows 95 activation key

        Returns:
            str: The Windows 95 key
        """

        def _generate_first():
            forbidden_numbers = [333, 444, 555, 666, 777, 888, 999]
            first = random.randint(100, 999)
            while first in forbidden_numbers:
                first = random.randint(100, 999)
            return str(first)

        def _generate_second():
            second_check = 8
            while second_check % 7 != 0:
                second = ""
                for i in range(0, 7):
                    number = random.randint(1, 9)
                    second += str(number)
                    second_check += number
            return second

        first = _generate_first()
        second = _generate_second()

        return f"{first}-{second}"


    @staticmethod
    def setclipboard(content: str) -> None:
        """Copies the content to clipboard
        Args:
            content (str): The content to be copied
        """
        pyperclip.copy(content)


    @staticmethod
    def getclipboard() -> str:
        """Copies the content to clipboard
        Returns:
            str: The content of the Clipboard
        """
        return pyperclip.paste()


    @staticmethod
    def order_dict(dictionary: dict, key: str, descending: bool = True) -> OrderedDict:
        """Order dictionary by key
        Args:
            dictionary (dict): The dictionary to be sorted
            key (str): The key to sort by
            descending (bool, optional): Sort by descending (default=True)
        """

        if isinstance(key, tuple):
            getter = lambda v: reduce(operator.getitem, key, v)
        else:
            getter = lambda v: v[key]
        return OrderedDict(sorted(dictionary.items(), key=lambda kv: getter(kv[1]), reverse=descending))


    @staticmethod
    def only_keep_x(dictionary: dict, amount: int) -> dict:
        """Only Keep first X Items in dictionary

        Args:
            dictionary (dict): The dictionary to be sorted
            amount (int): The amount of items to keep

        Returns:
            dict: The dictionary with only the first X items
        """

        return dict(list(dictionary.items())[:amount])


    @staticmethod
    def padleft(content: str, amount: int, char = " ") -> str:
        return content.rjust(amount, char)


    @staticmethod
    def padright(content: str, amount: int = 0, char = " ") -> str:
        return content.ljust(amount, char)


    @staticmethod
    def starts_with_any(text: str, prefixes: list):
        """Checks if a given string starts with any of the elements in a list of prefixes.

        Args:
            text (str): The string to check.
            prefixes (list): A list of strings to check as prefixes.
        Returns:
            bool: True if the text starts with any of the prefixes, False otherwise.
        """

        for prefix in prefixes:
            if text.startswith(prefix):
                return True
        return False


    @staticmethod
    def unix_timestamp() -> int:
        """Unix timestamp
        Returns: Unix timestamp
        """
        return int(time.time() * 1000)


    @staticmethod
    def build_query(params: Dict[str, Any]) -> str:
        """
        Build a query string with light OData-awareness.
        - Preserves $ keys like $select, $filter, $orderby, $top, $skiptoken.
        - Accepts list values for $select/$expand and joins with commas.
        - Does not re-encode already composed OData expressions if passed as strings.

        Examples:
            {"$select": ["id", "displayName"], "$top": 50}
            -> "$select=id,displayName&$top=50"

            {"$filter": "startswith(displayName,'A')", "$orderby": "displayName asc"}
            -> "$filter=startswith(displayName,'A')&$orderby=displayName asc"
        """

        if not params:
            return ""

        # Special Keys
        comma_join_keys = {"$select", "$expand", "$orderby"}
        odata_keys = {"$select", "$expand", "$filter", "$orderby", "$search", "$top", "$skip", "$skiptoken", "$count"}

        parts: list[str] = []

        for key, val in params.items():
            if val is None:
                continue

            if key in comma_join_keys and isinstance(val, (list, tuple)):
                value_str = ",".join(str(x) for x in val)
            else:
                if isinstance(val, (list, tuple)) and key not in odata_keys:
                    for item in val:
                        if item is None: continue
                        parts.append(f"{quote(str(key), safe='$')}={quote(str(item), safe='$,()' )}")
                    continue
                value_str = str(val)

            # Encode value but allow common OData token characters unescaped for readability:
            # - $ in case value contains tokens (rare)
            # - , (commas for $select/$expand)
            # - () often used in functions: startswith(), any(), etc.
            # - ' ' space will be encoded as %20 by quote
            encoded_key = quote(str(key), safe="$")
            encoded_val = quote(value_str, safe="$,()'/:")  # allow slashes e.g., drive/root:/path:
            parts.append(f"{encoded_key}={encoded_val}")

        return "&".join(parts)


    #region AI VIBE CODE SLOP
    @staticmethod
    def table_from_rows(
        rows: List[Mapping[str, Any]],
        sort_key: str,
        include_columns: Optional[Sequence[str]] = None,
    ) -> Table:
        """
        Build a Rich Table from a list of dicts.
        - If include_columns is provided and non-empty, only those columns (in order) are shown.
        - Otherwise, columns are inferred from the union of keys (order of first appearance).
        - Rows are sorted by `sort_key` ascending; None values are placed last.
        """
        rows = list(rows)

        # Determine columns
        if include_columns and len(include_columns) > 0:
            columns = list(include_columns)
        else:
            seen = {}
            for r in rows:
                for k in r.keys():
                    if k not in seen:
                        seen[k] = None
            columns = list(seen.keys())

        # Sort rows by sort_key (None last)
        def _sort_val(r: Mapping[str, Any]):
            v = r.get(sort_key, None)
            return (v is None, v)

        try:
            rows_sorted = sorted(rows, key=_sort_val)
        except TypeError:
            # Mixed incomparable types — fall back to string comparison
            def _safe(v):
                if v is None:
                    return (1, "")
                return (0, str(v))
            rows_sorted = sorted(rows, key=lambda r: _safe(r.get(sort_key)))

        # Build table
        table = Table()
        for col in columns:
            table.add_column(str(col), header_style="bold")

        for r in rows_sorted:
            table.add_row(
                *[("" if r.get(col) is None else str(r.get(col))) for col in columns]
            )

        return table
    #endregion


    @staticmethod
    def terminal_size() -> tuple[int, int]:
        """Get the size of the terminal
        Returns:
            tuple[int, int]: The width and height of the terminal
        """
        width, height = os.get_terminal_size()
        return width, height

