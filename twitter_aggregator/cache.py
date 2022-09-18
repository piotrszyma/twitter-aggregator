import re


RE_CACHE_IGNORED = re.compile(r"/2\/users\/\d+\/tweets")


def should_cache_url(url: str) -> bool:
    has_match = bool(RE_CACHE_IGNORED.search(url))
    return not has_match
