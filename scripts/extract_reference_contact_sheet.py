"""Extract representative frames from user-provided MP4 references."""

from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\liuzh\Desktop\1")
OUT = ROOT / "resource" / "fromAI" / "10_review_proxies" / "fromme_video_contact_sheet.png"
sources = [ROOT / "resource" / "fromme" / "3.mp4", ROOT / "resource" / "fromme" / "4.mp4"]
thumbs = []

for source in sources:
    container = av.open(str(source))
    duration = float(container.duration / av.time_base)
    for fraction in (0.1, 0.35, 0.65, 0.9):
        target = duration * fraction
        container.seek(int(target * av.time_base), backward=True)
        frame = next(container.decode(video=0))
        image = frame.to_image().convert("RGB")
        image.thumbnail((640, 340), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (660, 390), "black")
        canvas.paste(image, ((660 - image.width) // 2, 28))
        ImageDraw.Draw(canvas).text((12, 8), f"{source.name}  {target:.2f}s", fill="#E6E6E6")
        thumbs.append(canvas)
    container.close()

sheet = Image.new("RGB", (1320, 1560), "black")
for index, thumb in enumerate(thumbs):
    sheet.paste(thumb, ((index % 2) * 660, (index // 2) * 390))
OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT)
print(OUT)

