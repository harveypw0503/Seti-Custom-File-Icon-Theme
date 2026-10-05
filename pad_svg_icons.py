#!/usr/bin/env python3
#10/4/2026
#harveypw0503

"""
SVG Icon Padder
----------------
Batch-adds consistent visual padding to a folder of SVG icons by wrapping
their contents in a <g transform="translate(...) scale(...)"> group, sized
proportionally to each file's own viewBox. Works across mixed source sizes
(16x16, 32x32, 256x256, etc.) since the math is based on the viewBox, not a
fixed pixel offset.

Requires only the Python standard library (tkinter + xml.etree). On Linux,
if tkinter isn't installed: `sudo apt install python3-tk` (Debian/Ubuntu)
or the equivalent for your distro. Windows/Mac python.org installers
already include it.

Run: python3 pad_svg_icons.py
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

# Tags that should NOT be wrapped/transformed — they're non-visual or
# define reusable content rather than render it directly.
SKIP_TAGS = {"defs", "style", "title", "desc", "metadata"}

MARKER_ATTR = "data-icon-pad"


def qname(tag):
    """Strip namespace braces for simple comparisons, e.g. '{ns}path' -> 'path'."""
    return tag.split("}")[-1] if "}" in tag else tag


def parse_viewbox(root):
    """Return (minx, miny, width, height) from the SVG's viewBox, falling
    back to width/height attributes, then a generic 0 0 100 100."""
    vb = root.get("viewBox")
    if vb:
        parts = re.split(r"[ ,]+", vb.strip())
        if len(parts) == 4:
            try:
                return tuple(float(p) for p in parts)
            except ValueError:
                pass
    w = root.get("width", "100")
    h = root.get("height", "100")
    try:
        w = float(re.sub(r"[^0-9.]", "", w) or 100)
        h = float(re.sub(r"[^0-9.]", "", h) or 100)
    except ValueError:
        w, h = 100.0, 100.0
    return (0.0, 0.0, w, h)


def already_padded(root):
    for child in root:
        if qname(child.tag) == "g" and child.get(MARKER_ATTR) == "1":
            return True
    return False


def pad_svg_file(path, scale):
    """Wrap this SVG's visual content in a centered, scaled <g>. Returns
    a short status string describing what happened."""
    tree = ET.parse(path)
    root = tree.getroot()

    if qname(root.tag) != "svg":
        return "skipped (not an <svg> root)"

    if already_padded(root):
        return "skipped (already padded)"

    minx, miny, width, height = parse_viewbox(root)

    # Centered scale transform, derived from this file's own viewBox so a
    # 16x16 icon and a 256x256 icon both get the same proportional margin.
    tx = (1 - scale) * (minx + width / 2)
    ty = (1 - scale) * (miny + height / 2)

    # Collect the direct children that should move into the wrapper,
    # leaving defs/style/title/desc/metadata where they are.
    movable = [c for c in list(root) if qname(c.tag) not in SKIP_TAGS]
    if not movable:
        return "skipped (nothing to wrap)"

    wrapper = ET.Element(f"{{{SVG_NS}}}g")
    wrapper.set("transform", f"translate({tx:.4f},{ty:.4f}) scale({scale})")
    wrapper.set(MARKER_ATTR, "1")  # marks this file as already processed

    for child in movable:
        root.remove(child)
        wrapper.append(child)
    root.append(wrapper)

    shutil.copy2(path, path + ".bak")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return "padded"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SVG Icon Padder")
        self.geometry("560x420")
        self.files = []

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="Select SVG Files...", command=self.pick_files).pack(side="left")
        ttk.Button(top, text="Select Folder...", command=self.pick_folder).pack(side="left", padx=6)

        self.count_label = ttk.Label(top, text="No files selected")
        self.count_label.pack(side="left", padx=10)

        scale_frame = ttk.Frame(self, padding=(10, 0))
        scale_frame.pack(fill="x")
        ttk.Label(scale_frame, text="Content scale (smaller = more padding):").pack(side="left")
        self.scale_var = tk.DoubleVar(value=0.75)
        ttk.Entry(scale_frame, textvariable=self.scale_var, width=6).pack(side="left", padx=6)
        ttk.Label(scale_frame, text="(e.g. 0.75 = 25% margin on each side)").pack(side="left")

        ttk.Button(self, text="Pad Selected Icons", command=self.run).pack(pady=10)

        ttk.Label(self, text="Log:").pack(anchor="w", padx=10)
        self.log = tk.Text(self, height=14)
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        note = ("Each file is backed up as <name>.svg.bak before being modified. "
                "Already-padded files are skipped automatically, so it's safe to "
                "re-run this on a folder you've partially processed.")
        ttk.Label(self, text=note, wraplength=540, foreground="#555").pack(padx=10, pady=(0, 10))

    def pick_files(self):
        paths = filedialog.askopenfilenames(
            title="Select SVG icons", filetypes=[("SVG files", "*.svg")]
        )
        if paths:
            self.files = list(paths)
            self.count_label.config(text=f"{len(self.files)} file(s) selected")

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select folder of SVG icons")
        if folder:
            self.files = [
                os.path.join(folder, f) for f in sorted(os.listdir(folder))
                if f.lower().endswith(".svg")
            ]
            self.count_label.config(text=f"{len(self.files)} file(s) found in folder")

    def run(self):
        if not self.files:
            messagebox.showinfo("No files", "Select some SVG files or a folder first.")
            return
        try:
            scale = float(self.scale_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid scale", "Scale must be a number, e.g. 0.75")
            return
        if not (0 < scale < 1):
            messagebox.showerror("Invalid scale", "Scale should be between 0 and 1.")
            return

        self.log.delete("1.0", tk.END)
        ok, skipped, failed = 0, 0, 0
        for path in self.files:
            name = os.path.basename(path)
            try:
                status = pad_svg_file(path, scale)
                self.log.insert(tk.END, f"{name}: {status}\n")
                if status == "padded":
                    ok += 1
                else:
                    skipped += 1
            except Exception as e:
                self.log.insert(tk.END, f"{name}: FAILED - {e}\n")
                failed += 1
            self.log.see(tk.END)
            self.update_idletasks()

        self.log.insert(tk.END, f"\nDone. {ok} padded, {skipped} skipped, {failed} failed.\n")
        self.log.see(tk.END)


if __name__ == "__main__":
    App().mainloop()
