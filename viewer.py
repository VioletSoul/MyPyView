import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

THUMB_SIZE = (80, 80)
THUMB_MARGIN = 10
THUMB_BORDER = 4
THUMB_BG = "#222"
THUMB_ACTIVE_BG = "#444"
THUMB_OUTLINE = "#fff"
THUMB_ACTIVE_OUTLINE = "#ff9800"
THUMB_CENTER_BOX = "#888"
THUMB_CENTER_BOX_WIDTH = 3

def get_mouse_wheel_delta(event):
    # Универсально для Windows (±120), macOS (±1), Linux (event.num)
    if hasattr(event, 'delta') and event.delta != 0:
        print(f'[DEBUG] event.delta={event.delta}')
        return int(event.delta / abs(event.delta))
    elif hasattr(event, 'num'):
        print(f'[DEBUG] event.num={event.num}')
        if event.num == 4:
            return 1
        elif event.num == 5:
            return -1
    return 0

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1000x800")
        self.root.minsize(700, 500)
        self.root.configure(bg="#222")

        self.images = []
        self.thumbnails = []
        self.index = 0
        self.fullscreen = False
        self.original_image = None
        self.original_size = (0, 0)
        self.zoom = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.drag_start = None
        self.drag_offset = (0, 0)
        self.zoom_cache = {}

        self._mouse_over_main = False
        self._mouse_over_thumb = False

        # Меню
        menubar = tk.Menu(self.root, bg="#222", fg="#fff",
                          activebackground="#333", activeforeground="#fff", tearoff=0)
        file_menu = tk.Menu(menubar, tearoff=0, bg="#222", fg="#fff",
                            activebackground="#333", activeforeground="#fff")
        file_menu.add_command(label="Открыть папку", command=self.open_folder)
        menubar.add_cascade(label="Файл", menu=file_menu)
        view_menu = tk.Menu(menubar, tearoff=0, bg="#222", fg="#fff",
                            activebackground="#333", activeforeground="#fff")
        view_menu.add_command(label="Увеличить", command=self.zoom_in)
        view_menu.add_command(label="Уменьшить", command=self.zoom_out)
        menubar.add_cascade(label="Масштаб", menu=view_menu)
        self.root.config(menu=menubar)

        # Область изображения
        self.image_canvas = tk.Canvas(self.root, bg="#222",
                                      highlightthickness=0, bd=0, cursor="fleur")
        self.image_canvas.pack(fill="both", expand=True)
        self.image_canvas.bind("<Double-Button-1>", self.toggle_fullscreen)
        self.image_canvas.bind("<Configure>", self.on_resize)
        self.image_canvas.bind("<ButtonPress-1>", self._start_drag)
        self.image_canvas.bind("<B1-Motion>", self._on_drag)
        self.image_canvas.bind("<ButtonRelease-1>", self._end_drag)
        self.image_canvas.bind("<Enter>", self._on_main_enter)
        self.image_canvas.bind("<Leave>", self._on_main_leave)
        self.image_canvas.bind("<MouseWheel>", self._on_main_wheel)
        self.image_canvas.bind("<Button-4>", self._on_main_wheel)
        self.image_canvas.bind("<Button-5>", self._on_main_wheel)

        # Канвас миниатюр
        self.thumb_canvas = tk.Canvas(self.root,
                                      height=THUMB_SIZE[1] + 2*THUMB_MARGIN,
                                      bg="#222", highlightthickness=0, bd=0)
        self.thumb_canvas.pack(fill="x", side="bottom")
        self.thumb_canvas.bind("<Configure>", self._on_thumb_configure)
        self.thumb_canvas.bind("<Enter>", self._on_thumb_enter)
        self.thumb_canvas.bind("<Leave>", self._on_thumb_leave)
        self.thumb_canvas.bind("<MouseWheel>", self._on_thumb_wheel)
        self.thumb_canvas.bind("<Button-4>", self._on_thumb_wheel)
        self.thumb_canvas.bind("<Button-5>", self._on_thumb_wheel)
        self.thumb_canvas.config(xscrollincrement=1)

        self.status_bar = tk.Label(
            self.root,
            text="",
            anchor="w",
            bg="#222",
            fg="#fff",
            font=("Arial", 11),
            padx=8, pady=6
        )
        self.status_bar.pack(side="bottom", fill="x")

        self.thumb_offset = 0

    def open_folder(self):
        default_dir = str(Path.home() / "Pictures")
        folder = filedialog.askdirectory(initialdir=default_dir)
        if folder:
            print(f"[DEBUG] Открыта папка: {folder}")
            self.images = []
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"):
                self.images.extend(glob.glob(os.path.join(folder, ext)))
            self.images.sort()
            self.index = 0
            self.thumb_offset = 0
            self.zoom_cache = {}
            if self.images:
                print(f"[DEBUG] Найдено изображений: {len(self.images)}")
                self._generate_thumbnails()
                self.load_image()
                self.show_image()
                self._draw_thumbnails()
            else:
                print("[DEBUG] Нет изображений.")
                messagebox.showinfo("Нет изображений", "В выбранной папке нет поддерживаемых изображений.")

    def _generate_thumbnails(self):
        self.thumbnails = []
        for img_path in self.images:
            try:
                img = Image.open(img_path)
                thumb = img.copy()
                thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
                thumb_img = ImageTk.PhotoImage(thumb)
                self.thumbnails.append(thumb_img)
            except Exception as ex:
                print(f"[DEBUG] Не удалось сделать миниатюру {img_path}: {ex}")
                self.thumbnails.append(None)

    def _draw_thumbnails(self):
        self.thumb_canvas.delete("all")
        canvas_width = self.thumb_canvas.winfo_width()
        thumb_w = THUMB_SIZE[0] + 2*THUMB_BORDER + THUMB_MARGIN
        center_x = canvas_width // 2
        for i, thumb_img in enumerate(self.thumbnails):
            offset = (i - self.index) * thumb_w + center_x - THUMB_SIZE[0]//2
            y = THUMB_MARGIN
            if thumb_img:
                rect = self.thumb_canvas.create_rectangle(
                    offset-THUMB_BORDER, y-THUMB_BORDER,
                    offset+THUMB_SIZE[0]+THUMB_BORDER, y+THUMB_SIZE[1]+THUMB_BORDER,
                    fill=THUMB_ACTIVE_BG if i == self.index else THUMB_BG,
                    outline=THUMB_ACTIVE_OUTLINE if i == self.index else THUMB_OUTLINE,
                    width=2 if i == self.index else 1
                )
                img_id = self.thumb_canvas.create_image(
                    offset, y, anchor="nw", image=thumb_img
                )
                self.thumb_canvas.tag_bind(img_id, "<Button-1>", lambda e, idx=i: self._select_image(idx))
                self.thumb_canvas.tag_bind(rect, "<Button-1>", lambda e, idx=i: self._select_image(idx))
        box_x0 = center_x - THUMB_SIZE[0]//2 - THUMB_BORDER
        box_y0 = THUMB_MARGIN - THUMB_BORDER
        box_x1 = center_x + THUMB_SIZE[0]//2 + THUMB_BORDER
        box_y1 = THUMB_MARGIN + THUMB_SIZE[1] + THUMB_BORDER
        self.thumb_canvas.create_rectangle(
            box_x0, box_y0, box_x1, box_y1,
            outline=THUMB_CENTER_BOX, width=THUMB_CENTER_BOX_WIDTH
        )

    def _select_image(self, idx):
        print(f"[DEBUG] Клик по миниатюре: {idx}")
        if 0 <= idx < len(self.images):
            self.index = idx
            self.zoom = 1.0
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.zoom_cache = {}
            self.load_image()
            self.show_image()
            self._draw_thumbnails()

    def load_image(self):
        if not self.images:
            return
        try:
            print(f"[DEBUG] Загружаем изображение: {self.images[self.index]}")
            self.original_image = Image.open(self.images[self.index])
            self.original_size = self.original_image.size
            print(f"[DEBUG] Оригинальный размер: {self.original_size}")
        except Exception as e:
            print(f"[DEBUG] Ошибка загрузки: {e}")
            self.original_image = None
            self.original_size = (0, 0)
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{e}")

    def show_image(self):
        self.image_canvas.delete("all")
        if not self.images or not self.original_image:
            print("[DEBUG] Нет изображения для показа.")
            return
        win_w = self.image_canvas.winfo_width()
        win_h = self.image_canvas.winfo_height()
        img_w, img_h = self.original_size

        print(f"[DEBUG] Окно={win_w}x{win_h}, img={img_w}x{img_h}, zoom={self.zoom:.2f}")

        display_w, display_h = int(img_w * self.zoom), int(img_h * self.zoom)

        if self.zoom == 1.0 and (img_w > win_w or img_h > win_h):
            ratio = min(win_w / img_w, win_h / img_h)
            display_w, display_h = int(img_w * ratio), int(img_h * ratio)
            print(f"[DEBUG] AUTO-вписываю, ratio={ratio:.2f}, {display_w}x{display_h}")
        elif self.zoom == 1.0:
            display_w, display_h = img_w, img_h
            print(f"[DEBUG] Показываю оригинал {display_w}x{display_h}")

        cache_key = (self.index, display_w, display_h)
        if cache_key in self.zoom_cache:
            img = self.zoom_cache[cache_key]
        else:
            img = self.original_image.copy().resize((display_w, display_h), Image.LANCZOS)
            self.zoom_cache[cache_key] = img
            if len(self.zoom_cache) > 10:
                self.zoom_cache.pop(next(iter(self.zoom_cache)))
        self.photo = ImageTk.PhotoImage(img)
        x = (win_w - display_w) // 2 + self.image_offset_x
        y = (win_h - display_h) // 2 + self.image_offset_y
        print(f"[DEBUG] Рисую x={x}, y={y}")
        self.image_canvas.create_image(x, y, anchor="nw", image=self.photo)
        filename = os.path.basename(self.images[self.index])
        self.status_bar.config(
            text=f"{filename}  [{self.index+1} из {len(self.images)}]  |  Zoom: {int(self.zoom*100)}%, Размер: {display_w}×{display_h}"
        )
        self.root.title(f"Просмотрщик — {filename}")

    def next_image(self):
        if self.images and self.index < len(self.images) - 1:
            print(f"[DEBUG] Следующее изображение {self.index+1}")
            self.index += 1
            self.zoom = 1.0
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.zoom_cache = {}
            self.load_image()
            self.show_image()
            self._draw_thumbnails()

    def prev_image(self):
        if self.images and self.index > 0:
            print(f"[DEBUG] Предыдущее изображение {self.index-1}")
            self.index -= 1
            self.zoom = 1.0
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.zoom_cache = {}
            self.load_image()
            self.show_image()
            self._draw_thumbnails()

    def toggle_fullscreen(self, event=None):
        print(f"[DEBUG] FULLSCREEN: {'ON' if not self.fullscreen else 'OFF'}")
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def on_resize(self, event):
        print(f"[DEBUG] Resize: {event.width}x{event.height}")
        self.show_image()
        self._draw_thumbnails()

    def zoom_in(self):
        print(f"[DEBUG] Zoom IN, old={self.zoom}")
        old_zoom = self.zoom
        self.zoom = min(self.zoom * 1.1, 4.0)
        if abs(self.zoom - old_zoom) > 1e-3:
            self.show_image()

    def zoom_out(self):
        print(f"[DEBUG] Zoom OUT, old={self.zoom}")
        old_zoom = self.zoom
        self.zoom = max(self.zoom / 1.1, 0.1)
        if abs(self.zoom - old_zoom) > 1e-3:
            self.show_image()

    def _on_main_enter(self, event):
        print("[DEBUG] Мышь над картинкой")
        self._mouse_over_main = True

    def _on_main_leave(self, event):
        print("[DEBUG] Мышь УШЛА с картинки")
        self._mouse_over_main = False

    def _on_thumb_enter(self, event):
        print("[DEBUG] Мышь над миниатюрами")
        self._mouse_over_thumb = True

    def _on_thumb_leave(self, event):
        print("[DEBUG] Мышь УШЛА с миниатюр")
        self._mouse_over_thumb = False

    def _on_main_wheel(self, event):
        print(f"[DEBUG] MAIN WHEEL: vars={vars(event)}")
        if self._mouse_over_main and self.original_image:
            delta = get_mouse_wheel_delta(event)
            print(f"[DEBUG] MAIN WHEEL, delta={delta}")
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()

    def _on_thumb_wheel(self, event):
        print(f"[DEBUG] THUMB WHEEL: vars={vars(event)}")
        if self._mouse_over_thumb and self.images:
            delta = get_mouse_wheel_delta(event)
            print(f"[DEBUG] THUMB WHEEL, delta={delta}")
            if delta == 0:
                return
            # miniatures листать вниз — к следующим, поэтому delta отрицательно
            new_index = self.index + (-delta)
            if 0 <= new_index < len(self.images):
                self.index = new_index
                self.zoom = 1.0
                self.image_offset_x = 0
                self.image_offset_y = 0
                self.zoom_cache = {}
                self.load_image()
                self.show_image()
                self._draw_thumbnails()
        else:
            print("[DEBUG] WHEEL вне зоны миниатюр (игнор)")

    def _on_thumb_configure(self, event):
        self._draw_thumbnails()

    def _start_drag(self, event):
        self.drag_start = (event.x, event.y)
        self.drag_offset = (self.image_offset_x, self.image_offset_y)

    def _on_drag(self, event):
        if self.drag_start is not None:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.image_offset_x = self.drag_offset[0] + dx
            self.image_offset_y = self.drag_offset[1] + dy
            print(f"[DEBUG] Drag: dx={dx}, dy={dy}, offset=({self.image_offset_x},{self.image_offset_y})")
            self.show_image()

    def _end_drag(self, event):
        self.drag_start = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
