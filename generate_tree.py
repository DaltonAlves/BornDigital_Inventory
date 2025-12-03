import os
import mimetypes
import datetime
import math
import html
import traceback

# config
ROOT_DIR = r"/mnt/f/ms2215_accession2023_47"
OUTPUT_FILE = "index.html"
title = '2025-029'

#helpers/utils
def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    i = min(i, len(units) - 1)
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    s_str = f"{s}".rstrip("0").rstrip(".")
    return f"{s_str} {units[i]}"

def safe_mime(path):
    mime, _ = mimetypes.guess_type(path) #depreciated?
    return mime or "Unknown"

def format_dt(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def mime_category(mime):
    if mime.startswith("image"):
        return "image"
    elif mime.startswith("video"):
        return "video"
    elif mime.startswith("audio"):
        return "audio"
    #think this through more?
    elif mime in (
        "application/pdf", "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ):
        return "document"
    else:
        return "other"

def file_row(name, mime, size, last_modified):
    category = mime_category(mime)
    return (
        f"<li class='row file'>"
        f"<span class='cell name'>{html.escape(name)}</span>"
        f"<span class='cell mime {category}'>{html.escape(mime)}</span>"
        f"<span class='cell size'>{html.escape(size)}</span>"
        f"<span class='cell modified'>{html.escape(last_modified)}</span>"
        "</li>"
    )

def folder_block(folder_name, inner_html, stats):
    safe_id = html.escape(folder_name).replace(" ", "_")
    return (
        f"<li class='folder-block'>"
        f"<button class='folder-toggle' aria-expanded='false' aria-controls='{safe_id}-panel'>"
        f"<span class='disclosure'>▸</span>"
        f"<span class='folder-icon'>📁</span>"
        f"<span class='folder-name'>{html.escape(folder_name)}</span>"
        f"<span class='folder-stats'>{stats}</span>"
        "</button>"
        f"<ul id='{safe_id}-panel' class='nested' hidden>{inner_html}</ul>"
        "</li>"
    )

def build_directory_html(path):
    print(f"[DEBUG] entering build_directory_html with path: {path!r}")
    if not os.path.exists(path):
        print(f"[ERROR] path does not exist: {path!r}")
        return "", 0, 0
    if not os.path.isdir(path):
        print(f"[ERROR] path is not a directory: {path!r}")
        return "", 0, 0

    try:
        entries = sorted(os.listdir(path))
    except Exception as e:
        print(f"[EXCEPTION] os.listdir failed for {path!r}: {e}")
        traceback.print_exc()
        return "", 0, 0

    # show a small sample so logs don't explode for huge dirs
    print(f"[DEBUG] {len(entries)} entries found (showing up to 10): {entries[:10]}")

    files_html = []
    folders_html = []
    total_size = 0
    file_count = 0

    for entry in entries:
        # debug
        full_path = os.path.join(path, entry)
        # print a tiny debug for the very first few entries only
        if file_count < 3 and len(entries) < 20:
            print(f"[DEBUG] processing entry: {entry!r} -> {full_path!r}")

        if os.path.isdir(full_path):
            inner_html, sub_count, sub_size = build_directory_html(full_path)
            stats = f"{sub_count} files · {format_size(sub_size)}"
            folders_html.append(folder_block(entry, inner_html, stats))
            file_count += sub_count
            total_size += sub_size
        else:
            try:
                size = os.path.getsize(full_path)
                mime = safe_mime(full_path)
                modified = format_dt(os.path.getmtime(full_path))
                files_html.append(
                    file_row(entry, mime, format_size(size), modified)
                )
                file_count += 1
                total_size += size
            except Exception as e:
                # print and skip files we can't stat/read
                print(f"[WARN] failed to stat file {full_path!r}: {e}")
                traceback.print_exc()

    return "".join(folders_html + files_html), file_count, total_size

# static html (always the same)
html_head = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{title}</title>
<p class="subtitle">Example subtext...These files are not avaliable for online access. Please contact the Special Collections Research Center to arrange access...</p>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header>
<div class='search-bar'><input type='text' id='searchInput' placeholder='Search by file name or MIME type...'></div>
<div class='legend'><div>Name</div><div>MIME Type</div><div>Size</div><div>Last Modified</div></div>
</header>
<main><ul class='tree'>
"""

html_foot = """
</ul></main>
<script src="assets/script.js"></script>
</body>
</html>
"""

# Generate HTML
print(f"[INFO] ROOT_DIR = {ROOT_DIR!r}")
print(f"[INFO] exists: {os.path.exists(ROOT_DIR)}, isdir: {os.path.isdir(ROOT_DIR)}")
tree_html, count, size = build_directory_html(ROOT_DIR)
root_stats = f"{count} files · {format_size(size)}"
root_block = folder_block(os.path.basename(ROOT_DIR) or ROOT_DIR, tree_html, root_stats)

html_doc = html_head + root_block + html_foot

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_doc)

print(f"HTML inventory generated: {OUTPUT_FILE}")
