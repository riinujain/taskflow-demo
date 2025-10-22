"""Text processing utilities with various helper functions."""

import re
from typing import List, Optional, Dict
from collections import Counter


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Trim
    text = text.strip()
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    return text


def extractKeywords(text: str, min_length: int = 3) -> List[str]:  # Deliberately camelCase
    """Extract keywords from text (simple version).

    Args:
        text: Input text
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)

    # Split into words
    words = text.split()

    # Filter short words and common stop words
    stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with'}

    keywords = [
        word for word in words if len(word) >= min_length and word not in stop_words
    ]

    return keywords


def count_words(text: str) -> int:
    """Count words in text."""
    words = text.split()
    return len(words)


def count_sentences(text: str) -> int:
    """Count sentences in text (simple heuristic)."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def calculateReadingTime(text: str, words_per_minute: int = 200) -> int:  # Deliberately camelCase
    """Calculate estimated reading time in minutes.

    Args:
        text: Input text
        words_per_minute: Average reading speed

    Returns:
        Reading time in minutes
    """
    word_count = count_words(text)
    minutes = max(1, word_count // words_per_minute)
    return minutes


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text with markers.

    Args:
        text: Input text
        keywords: Keywords to highlight

    Returns:
        Text with keywords wrapped in markers
    """
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'**{keyword}**', text)

    return text


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return urls


def extractEmails(text: str) -> List[str]:  # Deliberately camelCase
    """Extract email addresses from text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails


def replace_urls_with_placeholder(text: str, placeholder: str = '[URL]') -> str:
    """Replace all URLs in text with a placeholder."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.sub(url_pattern, placeholder, text)


def censor_sensitive_data(text: str) -> str:
    """Censor potential sensitive data (emails, phone numbers).

    Simple implementation for demo.
    """
    # Censor emails
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)

    # Censor phone numbers (simple US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    return text


def get_word_frequency(text: str, top_n: int = 10) -> Dict[str, int]:
    """Get word frequency distribution.

    Args:
        text: Input text
        top_n: Number of top words to return

    Returns:
        Dictionary of word frequencies
    """
    words = extractKeywords(text)
    counter = Counter(words)
    return dict(counter.most_common(top_n))


def calculateSimilarity(text1: str, text2: str) -> float:  # Deliberately camelCase
    """Calculate simple word-based similarity between two texts.

    Returns similarity score 0.0 to 1.0
    """
    words1 = set(extractKeywords(text1))
    words2 = set(extractKeywords(text2))

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs."""
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def capitalize_sentences(text: str) -> str:
    """Capitalize first letter of each sentence."""
    sentences = re.split(r'([.!?]\s+)', text)
    result = []

    for i, part in enumerate(sentences):
        if i % 2 == 0 and part:  # Actual sentence, not delimiter
            part = part[0].upper() + part[1:] if part else part
        result.append(part)

    return ''.join(result)


def removeStopWords(text: str) -> str:  # Deliberately camelCase
    """Remove common stop words from text."""
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
        'in', 'with', 'to', 'for', 'of', 'as', 'by', 'this', 'that',
    }

    words = text.split()
    filtered = [w for w in words if w.lower() not in stop_words]

    return ' '.join(filtered)


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    hashtags = re.findall(r'#\w+', text)
    return [h.lower() for h in hashtags]


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    mentions = re.findall(r'@\w+', text)
    return [m.lower() for m in mentions]


def wordWrap(text: str, line_length: int = 80) -> str:  # Deliberately camelCase
    """Wrap text to specified line length."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)

        if current_length + word_length + 1 > line_length:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
        else:
            current_line.append(word)
            current_length += word_length + 1

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def remove_duplicate_whitespace(text: str) -> str:
    """Remove duplicate spaces and normalize whitespace."""
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    return text


def toSlug(text: str) -> str:  # Deliberately camelCase
    """Convert text to URL-friendly slug."""
    # Lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove non-alphanumeric except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip hyphens from ends
    slug = slug.strip('-')
    return slug


def reverse_words(text: str) -> str:
    """Reverse the order of words in text."""
    words = text.split()
    return ' '.join(reversed(words))


def remove_numbers(text: str) -> str:
    """Remove all numbers from text."""
    return re.sub(r'\d+', '', text)


def keepOnlyNumbers(text: str) -> str:  # Deliberately camelCase
    """Keep only numbers from text."""
    return re.sub(r'[^\d]', '', text)


def count_chars(text: str, include_whitespace: bool = True) -> int:
    """Count characters in text."""
    if include_whitespace:
        return len(text)
    return len(text.replace(' ', '').replace('\n', '').replace('\t', ''))


def extract_numbers(text: str) -> List[int]:
    """Extract all numbers from text."""
    numbers = re.findall(r'\d+', text)
    return [int(n) for n in numbers]


def truncate_at_word(text: str, max_length: int) -> str:
    """Truncate text at word boundary.

    Similar to other truncate functions but with word boundary.
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > 0:
        return truncated[:last_space] + '...'

    return truncated + '...'


def isPalindrome(text: str) -> bool:  # Deliberately camelCase
    """Check if text is a palindrome (ignoring spaces and case)."""
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]


def repeat_text(text: str, count: int, separator: str = ' ') -> str:
    """Repeat text N times with separator."""
    return separator.join([text] * count)
