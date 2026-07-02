from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import shutil
import time

app = Flask(__name__)

# --- CONFIG ---
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- UI LAYER ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crystal Fetch | Masterpiece</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #030712; background-image: radial-gradient(at 0% 0%, #1f1d2b 0, transparent 50%), radial-gradient(at 100% 100%, #171b36 0, transparent 50%); background-attachment: fixed; color: white; font-family: 'Inter', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .loader { border-top-color: #8b5cf6; animation: spinner 0.6s linear infinite; }
        @keyframes spinner { to { transform: rotate(360deg); } }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-6">
    <div class="glass w-full max-w-md rounded-3xl p-8 shadow-2xl">
        <h1 class="text-3xl font-bold text-center bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent mb-6">Crystal Fetch</h1>
        <form action="/download" method="POST" id="form" class="space-y-4">
            <input type="url" name="url" required placeholder="Paste YouTube link..." class="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-purple-500 transition-all">
            <select name="quality" class="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white">
                <option value="1080p">1080p (Best Video + Audio)</option>
                <option value="720p">720p (HD Video + Audio)</option>
                <option value="mp3">MP3 (High Quality Audio)</option>
            </select>
            <button type="submit" id="btn" class="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl font-bold transition-all">Initialize Download</button>
        </form>
        <div id="loader" class="hidden mt-6 text-center"><div class="loader inline-block w-8 h-8 border-4 border-white/10 rounded-full"></div><p class="text-xs text-slate-400 mt-2">Processing...</p></div>
    </div>
    <script>
        document.getElementById('form').onsubmit = () => {
            document.getElementById('btn').disabled = true;
            document.getElementById('loader').classList.remove('hidden');
        }
    </script>
</body>
</html>
'''

# --- BACKEND LOGIC ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    q = request.form.get('quality')
    
    # Clean old files to prevent server crash
    for f in os.listdir(DOWNLOAD_DIR):
        try: shutil.rm(os.path.join(DOWNLOAD_DIR, f))
        except: pass

    # Robust settings
    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
    }
    
    if q == '1080p':
        ydl_opts.update({'format': 'bestvideo[height<=1080]+bestaudio/bestvideo[height<=1080]/best'})
    elif q == '720p':
        ydl_opts.update({'format': 'bestvideo[height<=720]+bestaudio/bestvideo[height<=720]/best'})
    else:
        ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if q == 'mp3': filename = os.path.splitext(filename)[0] + '.mp3'
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
