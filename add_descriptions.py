#!/usr/bin/env python3
"""
Auto-generate meta descriptions for book reviews.
Extracts first 1-2 sentences from each review and adds to frontmatter.
"""

import os
import re
from pathlib import Path

def extract_description(content):
    """Extract first 1-2 sentences from markdown content."""
    # Remove markdown image syntax
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

    # Split into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())

    # Take first 1-2 sentences, max 160 chars for SEO
    description = ' '.join(sentences[:2])

    # Truncate if too long
    if len(description) > 160:
        description = description[:157] + '...'

    return description

def extract_keywords(title, content):
    """Generate keywords from title and content."""
    keywords = []

    # Extract author and book title from the title
    if ' by ' in title:
        book_part = title.split(' by ')[0].strip()
        author_part = title.split(' by ')[1].strip()
        keywords.append(book_part)
        keywords.append(author_part)

    # Add "book review" keyword
    keywords.append("book review")

    # Look for common topics in content
    topic_keywords = {
        'India': ['India', 'Indian history', 'Bharat'],
        'history': ['history'],
        'Mahabharata': ['Mahabharata', 'epic'],
        'Hindu': ['Hinduism', 'Hindu'],
        'economics': ['economics'],
        'politics': ['politics', 'political'],
        'philosophy': ['philosophy'],
        'biography': ['biography'],
        'fiction': ['fiction', 'novel'],
    }

    content_lower = content.lower()
    for key, values in topic_keywords.items():
        if key.lower() in content_lower:
            keywords.extend([v for v in values if v.lower() in content_lower][:2])

    # Return unique keywords, max 6
    seen = set()
    unique_keywords = []
    for k in keywords:
        if k.lower() not in seen:
            seen.add(k.lower())
            unique_keywords.append(k)

    return unique_keywords[:6]

def process_file(filepath):
    """Add description and keywords to a book review file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has description
    if 'description:' in content:
        print(f"✓ Skipping {filepath.name} (already has description)")
        return False

    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"✗ Skipping {filepath.name} (no frontmatter)")
        return False

    frontmatter = parts[1]
    body = parts[2].strip()

    # Extract title
    title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
    if not title_match:
        title_match = re.search(r"title:\s*'([^']+)'", frontmatter)

    if not title_match:
        print(f"✗ Skipping {filepath.name} (no title)")
        return False

    title = title_match.group(1)

    # Generate description and keywords
    description = extract_description(body)
    keywords = extract_keywords(title, body)

    # Add to frontmatter (before the closing ---)
    new_frontmatter = frontmatter.rstrip()
    new_frontmatter += f'\ndescription: "{description}"'
    new_frontmatter += f'\nkeywords: {keywords}'

    # Reconstruct file
    new_content = f"---{new_frontmatter}\n---\n\n{body}\n"

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Updated {filepath.name}")
    return True

def main():
    book_reviews_dir = Path('content/book-reviews')

    if not book_reviews_dir.exists():
        print("Error: content/book-reviews directory not found")
        return

    files = list(book_reviews_dir.glob('*.md'))
    print(f"Found {len(files)} book review files\n")

    updated = 0
    for filepath in sorted(files):
        if process_file(filepath):
            updated += 1

    print(f"\n✓ Updated {updated} files")
    print(f"✓ Skipped {len(files) - updated} files")

if __name__ == '__main__':
    main()
