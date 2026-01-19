// Global search index
let searchIndex = [];

// Load search index
async function loadSearchIndex() {
  try {
    const response = await fetch('/index.json');
    searchIndex = await response.json();
  } catch (error) {
    console.error('Error loading search index:', error);
  }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', function() {
  loadSearchIndex();

  // Search icon toggle
  const searchIcon = document.getElementById('search-icon');
  const searchContainer = document.getElementById('search-container');
  const globalSearch = document.getElementById('global-search');

  if (searchIcon && searchContainer) {
    searchIcon.addEventListener('click', function(e) {
      e.preventDefault();
      if (searchContainer.style.display === 'none' || searchContainer.style.display === '') {
        searchContainer.style.display = 'block';
        globalSearch.focus();
      } else {
        searchContainer.style.display = 'none';
        document.getElementById('search-results').style.display = 'none';
      }
    });
  }

  // Global search functionality
  if (globalSearch) {
    globalSearch.addEventListener('input', performGlobalSearch);

    // Close search when clicking outside
    document.addEventListener('click', function(event) {
      if (searchContainer && !searchContainer.contains(event.target) &&
          event.target !== searchIcon && !searchIcon.contains(event.target)) {
        searchContainer.style.display = 'none';
        document.getElementById('search-results').style.display = 'none';
      }
    });
  }

  // Book filter icon toggle
  const bookFilterIcon = document.getElementById('book-filter-icon');
  const filterDropdown = document.getElementById('filter-dropdown');

  if (bookFilterIcon && filterDropdown) {
    bookFilterIcon.addEventListener('click', function(e) {
      e.preventDefault();
      if (filterDropdown.style.display === 'none' || filterDropdown.style.display === '') {
        filterDropdown.style.display = 'block';
      } else {
        filterDropdown.style.display = 'none';
      }
    });
  }

  // Book reviews rating filter
  const ratingFilter = document.getElementById('rating-filter');
  if (ratingFilter) {
    ratingFilter.addEventListener('change', filterBookReviews);
  }
});

// Global search function
function performGlobalSearch() {
  const query = document.getElementById('global-search').value.toLowerCase().trim();
  const resultsContainer = document.getElementById('search-results');

  if (query.length < 2) {
    resultsContainer.style.display = 'none';
    return;
  }

  const results = searchIndex.filter(item => {
    return item.title.toLowerCase().includes(query) ||
           item.content.toLowerCase().includes(query) ||
           (item.author && item.author.toLowerCase().includes(query));
  });

  if (results.length === 0) {
    resultsContainer.innerHTML = '<p style="color: #666;">No results found</p>';
    resultsContainer.style.display = 'block';
    return;
  }

  let html = '<div style="max-height: 350px; overflow-y: auto;">';
  results.slice(0, 10).forEach(result => {
    const snippet = getSnippet(result.content, query);
    const sectionLabel = getSectionLabel(result.section);
    html += `
      <div style="margin-bottom: 1.2em; padding-bottom: 1em; border-bottom: 1px solid #ddd;">
        <div style="font-size: 0.85em; color: #888; margin-bottom: 0.3em;">${sectionLabel}</div>
        <a href="${result.permalink}" style="font-weight: 600; color: #1a1a1a; text-decoration: none; font-size: 1.05em;">${result.title}</a>
        ${result.rating ? `<div style="color: #f39c12; font-size: 0.9em; margin-top: 0.2em;">${'★'.repeat(result.rating)}${'☆'.repeat(5-result.rating)}</div>` : ''}
        ${result.author ? `<div style="font-size: 0.9em; color: #666; margin-top: 0.2em;">by ${result.author}</div>` : ''}
        <p style="font-size: 0.9em; color: #555; margin-top: 0.4em;">${snippet}</p>
      </div>
    `;
  });
  html += '</div>';

  if (results.length > 10) {
    html += `<p style="color: #888; font-size: 0.9em; margin-top: 1em;">Showing 10 of ${results.length} results</p>`;
  }

  resultsContainer.innerHTML = html;
  resultsContainer.style.display = 'block';
}

// Get content snippet around search query
function getSnippet(content, query) {
  const lowerContent = content.toLowerCase();
  const index = lowerContent.indexOf(query.toLowerCase());

  if (index === -1) {
    return content.substring(0, 150) + '...';
  }

  const start = Math.max(0, index - 50);
  const end = Math.min(content.length, index + query.length + 100);
  let snippet = content.substring(start, end);

  if (start > 0) snippet = '...' + snippet;
  if (end < content.length) snippet = snippet + '...';

  return snippet;
}

// Get section label
function getSectionLabel(section) {
  const labels = {
    'book-reviews': 'Book Review',
    'posts': 'Essay',
    'thoughts': 'Reflection',
    'travel': 'Travel',
    'divya-desams': 'Divya Desam'
  };
  return labels[section] || section;
}

// Filter book reviews by rating
function filterBookReviews() {
  const selectedRating = document.getElementById('rating-filter').value;
  const reviewItems = document.querySelectorAll('.book-review-item');
  const noResults = document.getElementById('no-results');

  let visibleCount = 0;

  reviewItems.forEach(item => {
    const rating = item.getAttribute('data-rating');

    // Check rating filter
    if (selectedRating === '' || rating === selectedRating) {
      item.style.display = '';
      visibleCount++;
    } else {
      item.style.display = 'none';
    }
  });

  // Show/hide no results message
  if (visibleCount === 0) {
    noResults.style.display = 'block';
  } else {
    noResults.style.display = 'none';
  }
}
