import sys
import os

def main():
    try:
        import ytl
    except ImportError:
        print("ytl library is not installed")
        sys.exit(1)

    if len(sys.argv) < 4:
        print("Usage: download_ytl.py <url> <quality> <output_dir>")
        sys.exit(1)

    url = sys.argv[1].strip()
    requested_quality = sys.argv[2].strip()
    output_dir = sys.argv[3].strip()

    if not url:
        print("Empty URL")
        sys.exit(1)

    if not requested_quality:
        requested_quality = "best"

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        video = ytl.Video(url)
    except Exception as e:
        print("Failed to initialize video:", e)
        sys.exit(1)

    try:
        streams = video.streams
    except Exception as e:
        print("Failed to get streams:", e)
        sys.exit(1)

    selected_stream = None
    for s in streams:
        q = getattr(s, "quality", None)
        if q and str(q).lower() == requested_quality.lower():
            selected_stream = s
            break

    if selected_stream is None:
        sorted_streams = []
        for s in streams:
            q = getattr(s, "quality", None)
            if q is None:
                continue
            q_str = str(q)
            num_part = ""
            for ch in q_str:
                if ch.isdigit():
                    num_part += ch
            if not num_part:
                continue
            try:
                height = int(num_part)
            except ValueError:
                continue
            sorted_streams.append((height, s))
        if not sorted_streams:
            print("No suitable streams found")
            sys.exit(1)
        sorted_streams.sort(key=lambda x: x[0], reverse=True)
        selected_stream = sorted_streams[0][1]

    title = getattr(video, "title", None)
    if not title:
        title = "video"

    def safe_filename(name):
        invalid_chars = '<>:"/\\|?*'
        cleaned = "".join(c for c in name if c not in invalid_chars)
        cleaned = cleaned.strip()
        if not cleaned:
            cleaned = "video"
        return cleaned

    base_name = safe_filename(title)

    ext = ""
    for attr in ["extension", "ext", "file_extension"]:
        if hasattr(selected_stream, attr):
            value = getattr(selected_stream, attr)
            if value:
                ext = str(value)
                break
    if not ext:
        mimetype = getattr(selected_stream, "mime_type", None)
        if mimetype:
            if "mp4" in mimetype:
                ext = "mp4"
            elif "webm" in mimetype:
                ext = "webm"
            elif "mkv" in mimetype:
                ext = "mkv"
            else:
                ext = "mp4"
        else:
            ext = "mp4"

    if not ext.startswith("."):
        ext = "." + ext

    filename = base_name + ext
    final_path = os.path.join(output_dir, filename)

    try:
        selected_stream.download(output_path=output_dir, filename=filename)
    except TypeError:
        try:
            selected_stream.download(output_dir, filename)
        except Exception as e:
            print("Download failed:", e)
            sys.exit(1)
    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)

    print("Downloaded to:", final_path)

if __name__ == "__main__":
    main()
