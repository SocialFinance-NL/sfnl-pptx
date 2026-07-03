"""Render slides to PNG via PowerPoint COM (Windows default). LibreOffice is a
documented fallback only and is not implemented here."""
from __future__ import annotations

import sys
from pathlib import Path


def com_available() -> bool:
    """Return True if PowerPoint COM automation can be started, False otherwise.

    Guards all imports and COM calls in try/except; CoUninitialize always runs
    in the finally block.
    """
    try:
        import win32com.client  # noqa: F401
        import pythoncom
    except Exception:
        return False
    try:
        pythoncom.CoInitialize()
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Quit()
        return True
    except Exception:
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def render_deck(pptx_path, out_dir, slide_indices=None) -> list[Path]:
    """Export slides to PNG via COM.

    Parameters
    ----------
    pptx_path:
        Path to the .pptx file.
    out_dir:
        Directory where PNGs will be written (created if absent).
    slide_indices:
        0-based slide indices to export.  None (default) exports all slides.

    Returns
    -------
    list[Path]
        Paths of exported PNG files in the order they were exported.

    Notes
    -----
    COM Slides collection is 1-based, so we use ``i + 1`` when calling
    ``pres.Slides(i + 1)``.

    A single retry on ``Dispatch`` is attempted when the initial call raises a
    ``pywintypes.com_error`` with HRESULT ``0x80010001``
    (``RPC_E_CALL_REJECTED`` / "call was rejected by callee"), which can occur
    transiently when PowerPoint is still initialising its COM server.
    """
    import pythoncom
    import win32com.client
    import time

    pptx_path = Path(pptx_path).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    # Retry Dispatch once on transient COM rejection (0x80010001).
    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
    except Exception as exc:
        hresult = getattr(exc, "hresult", None)
        if hresult == -2147418111:  # 0x80010001 as signed int
            time.sleep(1)
            app = win32com.client.Dispatch("PowerPoint.Application")
        else:
            pythoncom.CoUninitialize()
            raise

    images: list[Path] = []
    try:
        pres = app.Presentations.Open(str(pptx_path), WithWindow=False)
        try:
            total = pres.Slides.Count
            targets = range(total) if slide_indices is None else slide_indices
            for i in targets:
                slide = pres.Slides(i + 1)  # COM is 1-based
                dest = out_dir / f"slide_{i + 1:02d}.png"
                slide.Export(str(dest), "PNG", 1280, 720)
                images.append(dest)
        finally:
            pres.Close()
    finally:
        app.Quit()
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
    return images


def assert_layout_gallery(pptx_path, expected_total_layouts: int) -> None:
    """Open ``pptx_path`` in real PowerPoint and confirm the New Slide / Layout
    gallery offers exactly ``expected_total_layouts`` layouts across all designs.

    This is the authoritative check for scripts.merge_template: python-pptx can
    parse OOXML that PowerPoint itself would flag with a "repair?" prompt, so only
    an actual PowerPoint open proves the merged masters/layouts are structurally
    sound and visible to the end user.

    Raises AssertionError on any mismatch or if PowerPoint reports the file needed
    repair.
    """
    import pythoncom
    import win32com.client

    pptx_path = Path(pptx_path).resolve()
    pythoncom.CoInitialize()
    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
        try:
            pres = app.Presentations.Open(str(pptx_path), WithWindow=False)
            try:
                total = sum(d.SlideMaster.CustomLayouts.Count for d in pres.Designs)
                if total != expected_total_layouts:
                    raise AssertionError(
                        f"expected {expected_total_layouts} layouts across "
                        f"{pres.Designs.Count} design(s), PowerPoint reports {total}"
                    )
            finally:
                pres.Close()
        finally:
            app.Quit()
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--assert-layouts":
        if len(sys.argv) < 4:
            print("Usage: python -m scripts.render --assert-layouts <deck.pptx> <expected_total>", file=sys.stderr)
            sys.exit(2)
        assert_layout_gallery(sys.argv[2], int(sys.argv[3]))
        print("layout gallery OK:", sys.argv[3], "layouts")
        sys.exit(0)
    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        ok = com_available()
        print("PowerPoint COM:", "available" if ok else "NOT available")
        if not ok:
            print(
                "Remediation: ensure Microsoft PowerPoint is installed and "
                "pywin32 is present."
            )
        sys.exit(0 if ok else 1)
    if len(sys.argv) < 3:
        print("Usage: python -m scripts.render <deck.pptx> <out_dir>", file=sys.stderr)
        sys.exit(2)
    deck, out = sys.argv[1], sys.argv[2]
    for p in render_deck(deck, out):
        print("rendered", p)
