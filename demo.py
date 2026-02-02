#!/usr/bin/env python3
"""
Generate index.html for GitHub Pages
Scans all subdirectories and creates a collapsible folder structure
with links to all HTML files.
"""

import os
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def scan_html_files(root_dir):
    """
    Recursively scan for HTML files and organize them by folder.
    Returns a nested dictionary structure representing the folder hierarchy.
    """
    root_path = Path(root_dir)
    html_files = defaultdict(list)

    # Find all HTML files
    for html_file in root_path.rglob("*.html"):
        # Skip the index.html itself
        if html_file.name == "index.html" and html_file.parent == root_path:
            continue

        # Get relative path from root
        rel_path = html_file.relative_to(root_path)
        folder = str(rel_path.parent)

        # Skip files in root directory
        if folder == ".":
            continue

        html_files[folder].append({
            'name': html_file.name,
            'path': str(rel_path).replace('\\', '/')
        })

    # Sort files in each folder
    for folder in html_files:
        html_files[folder].sort(key=lambda x: x['name'])

    return dict(html_files)


def build_folder_tree(html_files):
    """
    Build a hierarchical tree structure from flat folder paths.
    """
    tree = {}

    for folder_path, files in html_files.items():
        parts = folder_path.split(os.sep) if folder_path != '.' else []
        current = tree

        # Build nested structure
        for part in parts:
            if part not in current:
                current[part] = {'_files': [], '_children': {}}
            current = current[part]['_children']

        # Add files at the leaf level
        if parts:
            leaf = tree
            for part in parts[:-1]:
                leaf = leaf[part]['_children']
            leaf[parts[-1]]['_files'] = files

    return tree


def generate_html(html_files, repo_name="Article Demos"):
    """
    Generate the HTML content for index.html
    """
    # Sort folders alphabetically
    sorted_folders = sorted(html_files.keys())

    # Count total files
    total_files = sum(len(files) for files in html_files.values())
    total_folders = len(html_files)

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            background-color: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}

        h1 {{
            text-align: center;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        .stats {{
            text-align: center;
            color: #718096;
            margin-bottom: 30px;
            font-size: 1em;
        }}

        .folder-container {{
            margin-bottom: 15px;
            background-color: #f7fafc;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }}

        .folder-container:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .folder-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            transition: all 0.3s ease;
        }}

        .folder-header:hover {{
            background: linear-gradient(135deg, #5a67d8 0%, #6b46a1 100%);
        }}

        .folder-header .folder-icon {{
            margin-right: 10px;
            font-size: 1.2em;
        }}

        .folder-header .arrow {{
            transition: transform 0.3s ease;
            font-size: 0.9em;
        }}

        .folder-header.collapsed .arrow {{
            transform: rotate(-90deg);
        }}

        .file-list {{
            list-style: none;
            padding: 15px 20px;
            margin: 0;
            background-color: white;
        }}

        .file-list li {{
            margin: 10px 0;
        }}

        .file-list a {{
            text-decoration: none;
            color: #2d3748;
            display: flex;
            align-items: center;
            padding: 10px 15px;
            border-radius: 6px;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }}

        .file-list a:hover {{
            background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
            border-color: #667eea;
            transform: translateX(5px);
        }}

        .file-list a::before {{
            content: "📄";
            margin-right: 10px;
            font-size: 1.2em;
        }}

        .content {{
            display: block;
            overflow: hidden;
            max-height: 2000px;
            transition: max-height 0.3s ease;
        }}

        .content.collapsed {{
            max-height: 0;
        }}

        .file-count {{
            background-color: rgba(255, 255, 255, 0.2);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.9em;
            margin-left: 10px;
        }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            color: #718096;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗂️ {repo_name}</h1>
        <div class="stats">Total: {total_files} HTML files across {total_folders} folders</div>

"""

    # Generate folder sections
    for folder in sorted_folders:
        files = html_files[folder]
        file_count = len(files)

        html_template += f"""        <div class="folder-container">
            <div class="folder-header">
                <span>
                    <span class="folder-icon">📁</span>
                    {folder}
                    <span class="file-count">{file_count} files</span>
                </span>
                <span class="arrow">▼</span>
            </div>
            <div class="content">
                <ul class="file-list">
"""

        # Generate file links
        for file_info in files:
            html_template += f"""                    <li><a href="{file_info['path']}">{file_info['name']}</a></li>
"""

        html_template += """                </ul>
            </div>
        </div>

"""

    # Add JavaScript and closing tags
    html_template += f"""
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>

    <script>
        // Toggle folder sections
        document.querySelectorAll('.folder-header').forEach(header => {{
            header.addEventListener('click', function() {{
                this.classList.toggle('collapsed');
                this.nextElementSibling.classList.toggle('collapsed');
            }});
        }});

        // Expand all folders by default
        // If you want them collapsed by default, uncomment the lines below:
        // document.querySelectorAll('.folder-header').forEach(header => {{
        //     header.classList.add('collapsed');
        //     header.nextElementSibling.classList.add('collapsed');
        // }});
    </script>
</body>
</html>
"""

    return html_template


def main():
    """Main function to generate index.html"""
    # Get current directory
    current_dir = Path(__file__).parent

    print(f"Scanning directory: {current_dir}")

    # Scan for HTML files
    html_files = scan_html_files(current_dir)

    if not html_files:
        print("No HTML files found in subdirectories!")
        return

    print(f"Found {sum(len(f) for f in html_files.values())} HTML files in {len(html_files)} folders")

    # Generate HTML
    html_content = generate_html(html_files)

    # Write index.html
    output_path = current_dir / "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[OK] Successfully generated {output_path}")
    print(f"\nFolders included:")
    for folder in sorted(html_files.keys()):
        print(f"  - {folder} ({len(html_files[folder])} files)")

    # Git operations
    print("\n" + "="*50)
    print("Starting git operations...")
    print("="*50)

    try:
        # Git add
        print("\n[1/3] Adding changes to git...")
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] Git add successful")
        else:
            print(f"[ERROR] Git add failed: {result.stderr}")
            return

        # Git commit
        print("\n[2/3] Committing changes...")
        total_files = sum(len(files) for files in html_files.values())
        total_folders = len(html_files)

        commit_message = f"""Update index.html - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

- Regenerated index.html with {total_files} HTML files
- Updated folder structure across {total_folders} folders

Co-Authored-By: Claude (claude-sonnet-4.5) <noreply@anthropic.com>"""

        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] Git commit successful")
            print(f"Commit message:\n{result.stdout}")
        elif "nothing to commit" in result.stdout:
            print("[INFO] No changes to commit")
            return
        else:
            print(f"[ERROR] Git commit failed: {result.stderr}")
            return

        # Git push
        print("\n[3/3] Pushing to remote...")
        result = subprocess.run(
            ["git", "push"],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] Git push successful")
            print(result.stdout if result.stdout else "Changes pushed to remote repository")
        else:
            print(f"[ERROR] Git push failed: {result.stderr}")
            return

        print("\n" + "="*50)
        print("[SUCCESS] All operations completed!")
        print("="*50)

    except FileNotFoundError:
        print("[ERROR] Git is not installed or not in PATH")
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
