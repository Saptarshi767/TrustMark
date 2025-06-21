#!/usr/bin/env python3
"""
Script to add favicon links to all HTML templates
"""

import os
import re

def add_favicon_to_template(file_path):
    """Add favicon links to an HTML template file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if favicon is already present
    if 'favicon.svg' in content:
        print(f"✅ Favicon already present in {file_path}")
        return
    
    # Find the title tag and add favicon after it
    title_pattern = r'(<title>.*?</title>)'
    favicon_links = '''
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="{{ url_for(\'static\', filename=\'favicon.svg\') }}">
    <link rel="icon" type="image/x-icon" href="{{ url_for(\'static\', filename=\'favicon.ico\') }}">
    <link rel="apple-touch-icon" href="{{ url_for(\'static\', filename=\'favicon.svg\') }}">
    '''
    
    # Replace title with title + favicon
    new_content = re.sub(title_pattern, r'\1' + favicon_links, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Added favicon to {file_path}")

def main():
    """Add favicon to all HTML templates"""
    templates_dir = 'templates'
    
    # List of templates to update
    templates = [
        'search.html',
        'search_results.html', 
        'transaction_details.html',
        'flagged_stats.html'
    ]
    
    for template in templates:
        file_path = os.path.join(templates_dir, template)
        if os.path.exists(file_path):
            add_favicon_to_template(file_path)
        else:
            print(f"❌ Template not found: {file_path}")

if __name__ == "__main__":
    main() 