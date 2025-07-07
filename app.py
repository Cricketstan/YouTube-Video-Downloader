from flask import Flask, render_template, request, send_file
import yt_dlp, os, uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        type_ = request.form.get("type")
        uid = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{uid}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestaudio" if type_ == "audio" else "best",
        }

        if type_ == "audio":
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_path = ydl.prepare_filename(info)
                if type_ == "audio":
                    final_path = final_path.rsplit(".", 1)[0] + ".mp3"

            return send_file(final_path, as_attachment=True)
        except Exception as e:
            return f"<h2 style='color:red;'>Error: {e}</h2>"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
