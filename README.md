# MyPyView

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FFB300?logo=python)
![Pillow](https://img.shields.io/badge/Pillow-%E2%9C%93-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Repo Size](https://img.shields.io/github/repo-size/VioletSoul/MyPyView)
![Code Size](https://img.shields.io/github/languages/code-size/VioletSoul/MyPyView)

A minimalistic image viewer written in Python.  
Inspired by Picasa and classic viewers, with a focus on convenience, a beautiful dark interface, and user-friendly navigation.

---

## Features

- Image navigation even in large folders
- Dark interface: all elements styled, no white borders or scrollbars
- "Conveyor" thumbnail strip:  
  Thumbnails are always centered; the selection frame is fixed, and the strip scrolls smoothly left/right  
  Mouse wheel scrolls through images, and the active thumbnail is always in the center
- Resizable viewing area:  
  The main image always stays centered  
  When zoomed in, you can drag the image with the mouse
- Smooth zooming:  
  Zoom up to 400% (pixel-perfect, no smoothing for maximum speed)  
  Mouse wheel over the main image zooms in/out  
  Zoomed images are cached for performance
- Full keyboard and mouse support:  
  Arrow keys and mouse wheel for navigation  
  Double-click for fullscreen, Esc to exit fullscreen
- No visible scrollbars:  
  Thumbnails are scrolled only with the mouse wheel
- Status bar:  
  Shows filename, image number, and zoom level
- Cross-platform:  
  Works on Windows, macOS, and Linux

---

## Installation

1. Make sure you have Python 3.8 or newer.
2. Install Pillow:
```
   pip install pillow
```
---

## Usage

1. Save the script as viewer.py
2. Run:
```
   python viewer.py
```
3. Use the File → Open Folder menu to select a directory with images.
4. Navigate images using:
    - Mouse wheel (over thumbnails or image)
    - Arrow keys
    - Clicking on thumbnails
5. Zoom in/out:
    - Mouse wheel over the image, or use the Scale menu
    - Drag the image with the left mouse button when zoomed in
6. Double-click the image to enter fullscreen, press Esc to exit.

---

## Keyboard and Mouse Shortcuts

| Action                         | Shortcut/Mouse         |
|---------------------------------|-----------------------|
| Next/Previous image             | Mouse wheel (thumbnails), Left/Right arrow |
| Zoom in/out                     | Mouse wheel (main image), Scale menu       |
| Drag image (when zoomed)        | Hold and drag left mouse button            |
| Fullscreen mode                 | Double-click main image                    |
| Exit fullscreen                 | Esc                                        |
| Open folder                     | File → Open Folder                         |

---

## Technical Details

- Performance:  
  All scaled images are cached for instant re-display at the same zoom.
  Thumbnails are rendered only once per folder.
- Thumbnail strip:  
  Implemented as a single canvas for maximum speed.
  No visible scrollbars; scrolling is smooth and instant.
- Image rendering:  
  Uses Image.NEAREST for fast scaling and classic pixel look.
  No smoothing for maximum performance at high zoom.
- Memory management:  
  Cache for zoomed images is limited in size and resets when changing images.
- No external dependencies except Pillow.

---

## Known Limitations

- For extremely large images (e.g., >5000x5000 px), zooming and dragging may be less smooth due to Python/Tkinter limitations.
- If you need even more performance and animation smoothness, consider PyQt, PySide, or Kivy.

---

## [LICENSE](LICENSE)
