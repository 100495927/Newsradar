import fnmatch
from typing import Type
from .RSSParser import RSSParser
from .MinisterioDSAParser import MinisterioDSAParser

url_a_parser_dict: dict[str, Type[RSSParser]] = {
    "https://www.dsca.gob.es/*": MinisterioDSAParser
}

def url_a_parser(url: str) -> Type[RSSParser]:
    for url_pattern, parser_class in url_a_parser_dict.items():
        if fnmatch.fnmatch(url, url_pattern):
            return parser_class
            
    return RSSParser

__all__ = ["url_a_parser"]