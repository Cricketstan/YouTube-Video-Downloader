from flask import Flask, render_template, request, send_file
import yt_dlp, os, uuid

app = Flask(__name__)
DL = "downloads"
os.makedirs(DL, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        t = request.form['type']
        uid = str(uuid.uuid4())
        tmpl = os.path.join(DL, f"{uid}.%(ext)s")
        opts = {'outtmpl': tmpl, 'format': 'bestaudio' if t=='audio' else 'best'}
        if t=='audio':
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
            path = y.prepare_filename(info)
            if t=='audio':
                path = path.rsplit('.', 1)[0] + '.mp3'
        return send_file(path, as_attachment=True)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
