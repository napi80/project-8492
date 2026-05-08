import sys
import os
import ytl

def main():
    if len(sys.argv) < 4:
        print("Usage: download_ytl.py <url> <quality> <output_dir>")
        sys.exit(1)

    url = sys.argv[1].strip()
    requested_quality = sys.argv[2].strip().lower()
    output_dir = sys.argv[3].strip()

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    info = ytl.info(url)
    title = info.get("title", "video")
    formats = info.get("formats", [])
    selected = None
    for f in formats:
        if f.get("quality", "").lower() == requested_quality:
            selected = f
            break

    if selected is None:
        sorted_formats = []
        for f in formats:
            q = f.get("quality", "")
            num = "".join(ch for ch in q if ch.isdigit())
            if not num:
                continue
            try:
                height = int(num)
            except:
                continue
            sorted_formats.append((height, f))
        if not sorted_formats:
            print("No suitable formats found")
            sys.exit(1)
        sorted_formats.sort(key=lambda x: x[0], reverse=True)
        selected = sorted_formats[0][1]

    url_to_download = selected["url"]
    ext = selected.get("ext", "mp4")
    if not ext.startswith("."):
        ext = "." + ext

    filename = title.strip().replace("/", "_").replace("\\", "_") + ext
    output_path = os.path.join(output_dir, filename)

    ytl.download(url_to_download, output_path)

    print("Downloaded to:", output_path)

if __name__ == "__main__":
    main()
