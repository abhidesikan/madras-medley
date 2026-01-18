#!/usr/bin/env python3
"""
Import ratings from Goodreads CSV export to book review markdown files.
"""

import csv
import os
from pathlib import Path
import re

def normalize_title(title):
    """Normalize title for matching - remove subtitles, special chars."""
    # Take only the main title (before colon or dash)
    title = title.split(':')[0].split('–')[0].split('-')[0]
    # Remove special characters and normalize spacing
    title = re.sub(r'[^\w\s]', '', title.lower())
    title = ' '.join(title.split())
    return title

def add_rating_to_file(filepath, rating):
    """Add or update rating in a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Check if rating already exists
    if re.search(r'^rating:\s*\d', frontmatter, re.MULTILINE):
        # Update existing rating
        frontmatter = re.sub(
            r'^rating:\s*\d+',
            f'rating: {rating}',
            frontmatter,
            flags=re.MULTILINE
        )
    else:
        # Add rating after draft line
        lines = frontmatter.split('\n')
        new_lines = []
        added = False
        for line in lines:
            new_lines.append(line)
            if line.startswith('draft:') and not added:
                new_lines.append(f'rating: {rating}')
                added = True
        frontmatter = '\n'.join(new_lines)

    # Write back
    new_content = f'---{frontmatter}---{body}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    # Read Goodreads CSV
    csv_path = 'static/goodreads_library_export.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    # Build rating lookup by normalized title
    ratings = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['Title']
            rating = row['My Rating']

            # Only process rated books (rating > 0)
            if rating and int(rating) > 0:
                normalized = normalize_title(title)
                ratings[normalized] = int(rating)

    print(f"Found {len(ratings)} rated books in Goodreads export\n")

    # Process book review files
    reviews_dir = Path('content/book-reviews')
    updated = 0
    matched = 0

    for filepath in sorted(reviews_dir.glob('*.md')):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from frontmatter
        title_match = re.search(r'title:\s*"([^"]+)"', content)
        if not title_match:
            continue

        review_title = title_match.group(1)
        normalized = normalize_title(review_title)

        # Try to match with Goodreads
        if normalized in ratings:
            rating = ratings[normalized]
            if add_rating_to_file(filepath, rating):
                print(f"✓ {filepath.name}: {rating} stars - {review_title[:50]}")
                updated += 1
                matched += 1
        else:
            # Try partial match (first few words)
            words = normalized.split()[:3]  # First 3 words
            partial = ' '.join(words)

            for gr_title, rating in ratings.items():
                if gr_title.startswith(partial) or partial in gr_title:
                    if add_rating_to_file(filepath, rating):
                        print(f"✓ {filepath.name}: {rating} stars (partial match) - {review_title[:50]}")
                        updated += 1
                        matched += 1
                    break

    print(f"\n✓ Updated {updated} files with ratings")
    print(f"✓ {matched} books matched with Goodreads")
    print(f"✓ {len(list(reviews_dir.glob('*.md'))) - matched} books not found in Goodreads export")

if __name__ == '__main__':
    main()
