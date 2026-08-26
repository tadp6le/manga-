import os
import re
import io
import time
import zipfile
import requests
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

API_BASE = 'https://jumpg-webapi.tokyo-cdn.com/api'

# ---------- HELPERS ----------
def force_lowest_quality(url):
    """Replace /hi/ (high quality) with /sc/ (standard/low quality)"""
    return url.replace('/hi/', '/sc/')

def extract_title_id_from_url(url):
    """Extract numeric title ID from a MangaPlus title URL."""
    match = re.search(r'/titles/(\d+)', url)
    if match:
        return match.group(1)
    # If it's already a number, return it
    if url.isdigit():
        return url
    raise ValueError('Invalid title URL or ID. Expected format: https://mangaplus.shueisha.co.jp/titles/12345')

def get_chapters_from_api(title_id):
    """Fetch all chapters for a given title_id using the official API."""
    resp = requests.get(
        f'{API_BASE}/title_detail',
        params={'title_id': title_id},
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    chapters = data.get('data', {}).get('chapterList', [])
    if not chapters:
        raise RuntimeError('No chapters found. The title ID may be invalid or the API changed.')
    return chapters

def get_page_urls(chapter_id):
    """Get image URLs for a chapter, forcing lowest quality."""
    resp = requests.get(
        f'{API_BASE}/manga_viewer',
        params={'chapter_id': chapter_id},
        headers={**HEADERS, 'Referer': 'https://mangaplus.shueisha.co.jp/'},
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
    pages = data.get('data', {}).get('mangaViewer', {}).get('pages', [])
    if not pages:
        raise RuntimeError('No pages found. Invalid chapter ID?')
    urls = [force_lowest_quality(p['imageUrl']) for p in pages if 'imageUrl' in p]
    return urls

def download_image(url):
    """Download a single image with correct referer and delay."""
    time.sleep(0.5)  # the delay you asked for
    headers = {**HEADERS, 'Referer': 'https://mangaplus.shueisha.co.jp/'}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.content

def build_chapter_zip(chapter_id):
    """Download all pages and return a ZIP as BytesIO."""
    urls = get_page_urls(chapter_id)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, url in enumerate(urls, start=1):
            img_data = download_image(url)
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'
            filename = f'page_{idx:03d}.{ext}'
            zf.writestr(filename, img_data)
    zip_buffer.seek(0)
    return zip_buffer

# ---------- FLASK ROUTES ----------
@app.route('/', methods=['GET'])
def index():
    # Step 3: If chapter_id is given, download immediately
    chapter_id = request.args.get('chapter_id', '').strip()
    if chapter_id:
        try:
            zip_data = build_chapter_zip(chapter_id)
            return send_file(
                zip_data,
                as_attachment=True,
                download_name=f'chapter_{chapter_id}.zip',
import os
import re
import io
import time
import zipfile
import requests
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

API_BASE = 'https://jumpg-webapi.tokyo-cdn.com/api'

# ---------- HELPERS ----------
def force_lowest_quality(url):
    """Replace /hi/ (high quality) with /sc/ (standard/low quality)"""
    return url.replace('/hi/', '/sc/')

def extract_title_id_from_url(url):
    """Extract numeric title ID from a MangaPlus title URL."""
    match = re.search(r'/titles/(\d+)', url)
    if match:
        return match.group(1)
    # If it's already a plain number, return it
    if url.isdigit():
        return url
    raise ValueError('Invalid title URL or ID. Expected format: https://mangaplus.shueisha.co.jp/titles/12345')

def get_chapters_from_api(title_id):
    """Fetch all chapters for a given title_id using the official API."""
    resp = requests.get(
        f'{API_BASE}/title_detail',
        params={'title_id': title_id},  # Now this is always a pure number!
        headers=HEADERS,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    chapters = data.get('data', {}).get('chapterList', [])
    if not chapters:
        raise RuntimeError('No chapters found. The title ID may be invalid or the API changed.')
    return chapters

def get_page_urls(chapter_id):
    """Get image URLs for a chapter, forcing lowest quality."""
    resp = requests.get(
        f'{API_BASE}/manga_viewer',
        params={'chapter_id': chapter_id},
        headers={**HEADERS, 'Referer': 'https://mangaplus.shueisha.co.jp/'},
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
    pages = data.get('data', {}).get('mangaViewer', {}).get('pages', [])
    if not pages:
        raise RuntimeError('No pages found. Invalid chapter ID?')
    urls = [force_lowest_quality(p['imageUrl']) for p in pages if 'imageUrl' in p]
    return urls

def download_image(url):
    """Download a single image with correct referer and delay."""
    time.sleep(0.5)  # the delay you asked for
    headers = {**HEADERS, 'Referer': 'https://mangaplus.shueisha.co.jp/'}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.content

def build_chapter_zip(chapter_id):
    """Download all pages and return a ZIP as BytesIO."""
    urls = get_page_urls(chapter_id)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, url in enumerate(urls, start=1):
            img_data = download_image(url)
            ext = url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'
            filename = f'page_{idx:03d}.{ext}'
            zf.writestr(filename, img_data)
    zip_buffer.seek(0)
    return zip_buffer

# ---------- FLASK ROUTES ----------
@app.route('/', methods=['GET'])
def index():
    # Step 3: If chapter_id is given, download immediately
    chapter_id = request.args.get('chapter_id', '').strip()
    if chapter_id:
        try:
            zip_data = build_chapter_zip(chapter_id)
            return send_file(
                zip_data,
                as_attachment=True,
                download_name=f'chapter_{chapter_id}.zip',
                mimetype='application/zip'
            )
        except Exception as e:
            return f'<h3>Error downloading chapter</h3><p>{str(e)}</p><p><a href="/">← Go back</a></p>', 500

    # Step 2: Show chapters list
    raw_input = request.args.get('title_id', '').strip()
    if raw_input:
        try:
            # *** FIX IS RIGHT HERE ***
            # Extract the numeric ID from the URL (or just use it if it's a number)
            title_id = extract_title_id_from_url(raw_input)
            
            chapters = get_chapters_from_api(title_id)
            # Sort by chapter number (descending) to show newest first
            chapters.sort(key=lambda x: int(x.get('chapter', 0)), reverse=True)
            
            # Get title name for the header
            title_name = chapters[0].get('titleName', 'Chapters') if chapters else 'Chapters'
            
            html = f'<h2>📚 {title_name}</h2>'
            html += '<p style="color:#555;">Click a chapter to download it as a ZIP.</p>'
            html += '<ul style="list-style:none;padding:0;">'
            for ch in chapters:
                chapter_num = ch.get('chapter', '?')
                sub = ch.get('subTitle', '')
                name = f'Chapter {chapter_num}'
                if sub:
                    name += f' - {sub}'
                cid = ch['chapterId']
                html += f'<li style="margin:8px 0;"><a href="/?chapter_id={cid}" style="display:block;padding:12px;background:#f0f0f0;border-radius:8px;text-decoration:none;color:#000;">{name}</a></li>'
            html += '</ul><p><a href="/">← Enter another title URL</a></p>'
            return render_template_string(html)
        
        except ValueError as e:
            # Catch the specific error from extract_title_id_from_url
            return f'<h3>Invalid Input</h3><p>{str(e)}</p><p><a href="/">← Go back</a></p>', 400
        except Exception as e:
            return f'<h3>Error loading chapters</h3><p>{str(e)}</p><p><a href="/">← Go back</a></p>', 500

    # Step 1: Show input form for the title URL
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MangaPlus Downloader</title>
            <style>
                body { font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
                input { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #ccc; border-radius: 8px; box-sizing: border-box; }
                button { width: 100%; padding: 14px; margin-top: 10px; font-size: 18px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .info { color: #555; font-size: 14px; margin-top: 20px; text-align: center; }
                .example { color: #888; font-size: 13px; margin-top: 5px; text-align: center; }
            </style>
        </head>
        <body>
            <h1>📖 MangaPlus Downloader</h1>
            <p>Paste the URL of any manga series to see all available chapters.</p>
            <form method="GET" action="/">
                <input type="text" name="title_id" placeholder="e.g. https://mangaplus.shueisha.co.jp/titles/100015" required>
                <button type="submit">📋 Show Chapters</button>
            </form>
            <div class="example">Example: https://mangaplus.shueisha.co.jp/titles/100015 (Hunter x Hunter)</div>
            <div class="info">⚡ Downloads the smallest web quality to save data.<br>⏱️ Includes a small delay to avoid rate limits.</div>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
pterId']
                html += f'<li style="margin:8px 0;"><a href="/?chapter_id={cid}" style="display:block;padding:12px;background:#f0f0f0;border-radius:8px;text-decoration:none;color:#000;">{name}</a></li>'
            html += '</ul><p><a href="/">← Enter another title URL</a></p>'
            return render_template_string(html)
        except Exception as e:
            return f'<h3>Error loading chapters</h3><p>{str(e)}</p><p><a href="/">← Go back</a></p>', 500

    # Step 1: Show input form for the title URL
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MangaPlus Downloader</title>
            <style>
                body { font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
                input { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #ccc; border-radius: 8px; box-sizing: border-box; }
                button { width: 100%; padding: 14px; margin-top: 10px; font-size: 18px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .info { color: #555; font-size: 14px; margin-top: 20px; text-align: center; }
                .example { color: #888; font-size: 13px; margin-top: 5px; text-align: center; }
            </style>
        </head>
        <body>
            <h1>📖 MangaPlus Downloader</h1>
            <p>Paste the URL of any manga series to see all available chapters.</p>
            <form method="GET" action="/">
                <input type="text" name="title_id" placeholder="e.g. https://mangaplus.shueisha.co.jp/titles/100015" required>
                <button type="submit">📋 Show Chapters</button>
            </form>
            <div class="example">Example: https://mangaplus.shueisha.co.jp/titles/100015 (Hunter x Hunter)</div>
            <div class="info">⚡ Downloads the smallest web quality to save data.<br>⏱️ Includes a small delay to avoid rate limits.</div>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
