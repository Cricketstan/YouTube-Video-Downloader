from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        download_type = request.form.get("type")
        unique_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

        # Advanced yt-dlp options (no cookies.txt)
        ydl_opts = {
            "format": "bestaudio" if download_type == "audio" else "best",
            "outtmpl": output_template,
            "noplaylist": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "geo_bypass": True,
            "sleep_interval_requests": 1,
            "sleep_interval": 2,
            "ratelimit": 500000,  # ~500 KB/s to avoid block
            "source_address": "0.0.0.0",  # Force IPv4
            "quiet": True,
            "nocheckcertificate": True,
        }

        # If audio selected, convert to mp3
        if download_type == "audio":
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_path = ydl.prepare_filename(info)
                if download_type == "audio":
                    final_path = final_path.rsplit('.', 1)[0] + '.mp3'

            return send_file(final_path, as_attachment=True)

        except Exception as e:
            return f"<h2 style='color:red;'>Download Error: {e}</h2>"

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
