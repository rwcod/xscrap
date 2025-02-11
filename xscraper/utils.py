from urllib.parse import quote

def build_search_url(keyword: str) -> str:
    """Build X.com search URL for any keyword format"""
    # Remove existing encoding if present
    clean_keyword = keyword.lstrip('#$')
    
    # Detect keyword type
    if keyword.startswith('#'):
        encoded = f'%23{quote(clean_keyword)}'
    elif keyword.startswith('$'):
        encoded = f'%24{quote(clean_keyword)}'
    else:
        encoded = quote(clean_keyword)
    
    return f"https://x.com/search?q={encoded}&src=typed_query&f=top" 