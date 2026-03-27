"""Ids con las que nombrar a los parsers dentro de mongo"""
from ..parsers import MinisterioDSAParser, RSSParser
from bidict import bidict

mongo_parser_ids = bidict({
    "RSSParser": RSSParser,
    "MinisteriosDSAPArser": MinisterioDSAParser
})