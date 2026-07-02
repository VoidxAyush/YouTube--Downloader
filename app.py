from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)

# Masterpiece UI: Crystal/Glassmorphism Design
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crystal Fetch | Masterpiece Downloader</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            background-color: #030712; 
            background-image:
                radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%),
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.2) 0, transparent 50%),
                radial-gradient(at 100% 0%, hsla(339,49%,30%,0.2) 0, transparent 50%);
            background-attachment: fixed;
            color: white;
            font-family: system-ui, -apple-system, sans-serif;
        }
        
        .glass-panel {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        }
        
        .glass-input {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .glass-input:focus {
            background: rgba(0, 0, 0, 0.4);
            border-color: rgba(139, 92, 246, 0.5);
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.25);
            outline: none;
        }
        
        .glass-button {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.8) 0%, rgba(59, 130, 246, 0.8) 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        .glass-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.5);
        }
        
        .quality-radio:checked + label {
            background: rgba(139, 92, 246, 0.15);
            border-color: rgba(139, 92, 246, 0.6);
            box-shadow: inset 0 0 15px rgba(139, 92, 246, 0.15);
        }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 overflow-hidden relative">

    <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="glass-panel w-full max-w-lg rounded-[2rem] p-8 md:p-10 relative z-10">
        <div class="text-center mb-10">
            <h1 class="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-indigo-400 to-blue-400 mb-2 tracking-tight">
                CrystalFetch
            </h1>
            <p class="text-gray-400 text-sm tracking-widest uppercase font-medium">Premium Media Extractor</p>
        </div>

        <form action="/download" method="POST" id="dl-form" class="space-y-6">
            <div>
                <input type="url" name="url" required placeholder="Paste YouTube link here..." 
                       class="glass-input w-full rounded-2xl px-5 py-4 text-white placeholder-gray-500 text-lg">
            </div>

            <div class="grid grid-cols-3 gap-4">
                <div>
                    <input type="radio" name="quality" id="1080p" value="1080p" class="quality-radio hidden" checked>
                    <label for="1080p" class="glass-panel cursor-pointer flex flex-col items-center justify-center py-5 px-2 rounded-2xl transition-all hover:bg-white/5">
                        <span class="font-bold text-lg md:text-xl text-white">1080p</span>
                        <span class="text-xs text-indigo-300 mt-1 tracking-wider uppercase">Full HD</span>
                    </label>
                </div>
                <div>
                    <input type="radio" name="quality" id="720p" value="720p" class="quality-radio hidden">
                    <label for="720p" class="glass-panel cursor-pointer flex flex-col items-center justify-center py-5 px-2 rounded-2xl transition-all hover:bg-white/5">
                        <span class="font-bold text-lg md:text-xl text-white">720p</span>
                        <span class="text-xs text-indigo-300 mt-1 tracking-wider uppercase">Standard</span>
                    </label>
                </div>
                <div>
                    <input type="radio" name="quality" id="mp3" value="mp3" class="quality-radio hidden">
                    <label for="mp3" class="glass-panel cursor-pointer flex flex-col items-center justify-center py-5 px-2 rounded-2xl transition-all hover:bg-white/5">
                        <span class="font-bold text-lg md:text-xl text-white">MP3</span>
                        <span class="text-xs text-indigo-300 mt-1 tracking-wider uppercase">Audio</span>
                    </label>
                </div>
            </div>

            <button type="submit" id="submit-btn" class="glass-button w-full rounded-2xl py-4 font-bold text-white text-lg tracking-wide mt-4 flex justify-center items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Initialize Download
            </button>

            <div id="loader" class="hidden text-center mt-6 space-y-3">
                <div class="inline-block w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-400 rounded-full animate-spin"></div>
                <p class="text-indigo-300 text-sm font-medium animate-pulse tracking-wide">Processing media streams...</p>
            </div>
        </form>
    </div>

    <script>
        document.getElementById('dl-form').addEventListener('submit', (e) => {
            const btn = document.getElementById('submit-btn');
            const loader = document.getElementById('loader');
            
            btn.style.opacity = '0.4';
            btn.style.pointerEvents = 'none';
            btn.innerHTML = 'Extracting...';
            loader.classList.remove('hidden');

            setTimeout(() => {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg> Initialize Download';
                loader.classList.add('hidden');
            }, 10000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    quality = request.form.get('quality')
    
    # Notice the new 'cookiefile': 'cookies.txt' line in each block below!
    if quality == '1080p':
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'downloads/%(title)s_1080p.%(ext)s',
            'cookiefile': 'cookies.txt', 
        }
    elif quality == '720p':
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'downloads/%(title)s_720p.%(ext)s',
            'cookiefile': 'cookies.txt',
        }
    elif quality == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            if quality == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Backend Error: {str(e)}. (Ensure FFmpeg is installed for 1080p and MP3 processing)"

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(port=5000, debug=True)
