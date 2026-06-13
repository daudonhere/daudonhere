#!/usr/bin/env python3
import os
import requests
import json
from collections import defaultdict

def get_all_repositories(username, token):
    """Fetch all repositories for a user"""
    headers = {'Authorization': f'token {token}'}
    repos = []
    page = 1
    
    while True:
        url = f'https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=updated'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            break
        
        repos.extend(data)
        page += 1
    
    return repos

def get_repository_languages(username, repo_name, token):
    """Fetch language statistics for a repository"""
    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{username}/{repo_name}/languages'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch languages for {repo_name}: {e}")
        return {}

def format_bytes(bytes_count):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"

def create_progress_bar(percentage, width=20):
    """Create a visual progress bar using Unicode characters"""
    filled = int(width * percentage / 100)
    empty = width - filled
    return '█' * filled + '░' * empty

def generate_languages_table(all_languages):
    """Generate markdown table for languages"""
    if not all_languages:
        return "No language data available"
    
    total_bytes = sum(all_languages.values())
    
    # Sort by bytes (descending) and get top 10
    sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Color mapping for languages
    lang_colors = {
        'TypeScript': '#3178c6',
        'Python': '#3776ab',
        'JavaScript': '#f7df1e',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Java': '#007396',
        'Go': '#00add8',
        'Rust': '#ce422b',
        'C++': '#00599c',
        'C#': '#239120',
        'PHP': '#777bb4',
        'Ruby': '#cc342d',
        'Solidity': '#aa6746',
        'Lua': '#000080',
    }
    
    table = "| Language | Usage | Bytes |\n"
    table += "|----------|-------|-------|\n"
    
    for lang, bytes_count in sorted_langs:
        percentage = (bytes_count / total_bytes) * 100
        progress_bar = create_progress_bar(percentage, width=20)
        formatted_bytes = format_bytes(bytes_count)
        
        table += f"| {lang} | {progress_bar} {percentage:.1f}% | {formatted_bytes} |\n"
    
    return table

def update_readme(readme_path, languages_table):
    """Update README.md with languages table"""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the languages section
    start_marker = "### 📊 Most Languages Used\n"
    end_marker = "\n---"
    
    if start_marker in content:
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if end_idx != -1:
            new_content = (
                content[:start_idx] +
                "\n" + languages_table + "\n" +
                content[end_idx:]
            )
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ README.md updated successfully!")
            return True
    else:
        print("⚠️ Language section not found in README.md")
        return False

def main():
    # Get credentials from environment
    token = os.getenv('GITHUB_TOKEN')
    username = 'daudonhere'
    
    if not token:
        print("❌ GITHUB_TOKEN not found in environment variables")
        return
    
    print(f"🔍 Fetching repositories for {username}...")
    repos = get_all_repositories(username, token)
    print(f"✅ Found {len(repos)} repositories")
    
    # Aggregate languages from all repositories
    all_languages = defaultdict(int)
    
    print("📊 Fetching language statistics...")
    for i, repo in enumerate(repos, 1):
        repo_name = repo['name']
        print(f"  [{i}/{len(repos)}] {repo_name}...", end=' ')
        
        languages = get_repository_languages(username, repo_name, token)
        for lang, bytes_count in languages.items():
            all_languages[lang] += bytes_count
        
        print("✅")
    
    # Convert defaultdict to regular dict for processing
    all_languages = dict(all_languages)
    
    print(f"\n📈 Language Statistics:")
    print(f"   Total languages: {len(all_languages)}")
    print(f"   Total bytes: {format_bytes(sum(all_languages.values()))}")
    
    # Generate languages table
    languages_table = generate_languages_table(all_languages)
    
    # Update README.md
    readme_path = 'README.md'
    if os.path.exists(readme_path):
        update_readme(readme_path, languages_table)
    else:
        print(f"❌ {readme_path} not found")

if __name__ == '__main__':
    main()
