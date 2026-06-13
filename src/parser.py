from bs4 import BeautifulSoup
import re

def clean_email_html(html_content):
    """
    Cleans raw HTML email content into readable text.
    Extracts text and keeps important job links in markdown format.
    """
    if not html_content:
        return ""

    # Check if content is actually HTML. If not, just clean whitespace.
    if not re.search(r'<[a-z/][^>]*>', html_content, re.IGNORECASE):
        return _clean_whitespace(html_content)

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove style, script, head, link, and meta tags
    for tag in soup(["style", "script", "head", "title", "meta", "noscript", "svg"]):
        tag.decompose()

    # Format anchor tags (links) as Markdown links
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        link_text = _clean_whitespace(a.get_text())
        # Avoid links with empty text or tracking pixels
        if link_text and href and not href.startswith("mailto:") and not href.startswith("tel:"):
            # Limit very long URLs in text representations
            if len(href) > 250:
                href = href[:250] + "..."
            a.replace_with(f" [{link_text}]({href}) ")

    # Format list items to markdown lists
    for li in soup.find_all("li"):
        li_text = _clean_whitespace(li.get_text())
        if li_text:
            li.replace_with(f"\n* {li_text}\n")

    # Add spacing around blocks
    for block in soup.find_all(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]):
        block.insert_before("\n")
        block.insert_after("\n")

    # Get text
    text = soup.get_text()

    # Clean whitespace and multiple empty lines
    return _clean_whitespace(text)

def _clean_whitespace(text):
    # Standardize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace 3 or more consecutive newlines with 2 newlines (double spacing)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip whitespace from start/end of lines
    lines = [line.strip() for line in text.split("\n")]
    
    # Join non-empty lines, keeping paragraphs
    cleaned_text = "\n".join(lines)
    return cleaned_text.strip()
