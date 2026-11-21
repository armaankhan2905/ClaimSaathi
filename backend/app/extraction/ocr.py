"""OCR with RapidOCR (ONNX models bundled in the package, no system install needed).

The engine is loaded once, on first use, and shared. Lines are rebuilt from the detected
text boxes in reading order, with blank lines where there is a clear vertical gap.
"""

import logging
import threading
from dataclasses import dataclass
from statistics import median

import numpy as np

log = logging.getLogger(__name__)
_engine = None
_lock = threading.Lock()


@dataclass
class OcrResult:
    text: str
    confidence: float | None  # average over recognised boxes, 0..1


def _get_engine():
    global _engine
    if _engine is None:
        from rapidocr import RapidOCR

        # The angle classifier sometimes flips upright lines and garbles them; documents are
        # already upright (PDF rotation and photo EXIF orientation are applied before OCR).
        _engine = RapidOCR(params={"Global.use_cls": False, "Global.log_level": "warning"})
    return _engine


def ocr_image(image: np.ndarray) -> OcrResult:
    """`image` is an RGB (or RGBA/grey) uint8 array."""
    if image.ndim == 3 and image.shape[2] == 4:
        image = image[:, :, :3]
    with _lock:  # the ONNX session isn't guaranteed thread-safe
        result = _get_engine()(np.ascontiguousarray(image))
    if result is None or result.boxes is None or len(result.txts or ()) == 0:
        return OcrResult(text="", confidence=None)
    boxes = [np.asarray(b, dtype=float) for b in result.boxes]
    text = assemble_lines(boxes, list(result.txts))
    scores = [float(s) for s in result.scores]
    return OcrResult(text=text, confidence=round(sum(scores) / len(scores), 3))


def assemble_lines(boxes: list[np.ndarray], texts: list[str]) -> str:
    """Group text boxes (4 corner points each) into lines, top to bottom, left to right."""
    items = []
    for box, txt in zip(boxes, texts):
        ys, xs = box[:, 1], box[:, 0]
        items.append({"top": ys.min(), "bottom": ys.max(), "left": xs.min(), "text": txt.strip()})
    items = [i for i in items if i["text"]]
    if not items:
        return ""
    items.sort(key=lambda i: (i["top"] + i["bottom"]) / 2)

    lines: list[list[dict]] = []
    for it in items:
        mid = (it["top"] + it["bottom"]) / 2
        if lines:
            last = lines[-1]
            l_top = min(i["top"] for i in last)
            l_bottom = max(i["bottom"] for i in last)
            if l_top <= mid <= l_bottom:  # same visual line
                last.append(it)
                continue
        lines.append([it])

    heights = [max(i["bottom"] for i in l) - min(i["top"] for i in l) for l in lines]
    typical = median(heights) if heights else 0
    out: list[str] = []
    prev_bottom = None
    for line, h in zip(lines, heights):
        top = min(i["top"] for i in line)
        if prev_bottom is not None and typical and top - prev_bottom > 1.2 * typical:
            out.append("")  # paragraph break
        out.append(" ".join(i["text"] for i in sorted(line, key=lambda i: i["left"])))
        prev_bottom = max(i["bottom"] for i in line)
    return "\n".join(out)
