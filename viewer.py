import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотрщик изображений")
        self.root.geometry("900x700")
        self.root.minsize(600, 400)
        self.root.configure(bg="#222")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#222')
        style.configure('TLabel', background='#222', foreground='#fff')
        style.configure('TButton',
                        background='#333',
                        foreground='#fff',
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none')
        style.map('TButton',
                  background=[('active', '#444')],
                  foreground=[('active', '#fff')])

        self.images = []
        self.index = 0
        self.fullscreen = False
        self.original_image = None  # PIL.Image
        self.original_size = (0, 0)

        self.frame = ttk.Frame(root, padding=0)
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.image_label = ttk.Label(
            self.frame,
            anchor="center"
        )
        self.image_label.pack(fill="both", expand=True, padx=0, pady=0)
        self.image_label.bind("<Double-Button-1>", self.toggle_fullscreen)

        self.status_bar = ttk.Label(
            root,
            text="",
            anchor="w",
            relief="sunken"
        )
        self.status_bar.pack(side="bottom", fill="x")

        btn_frame = ttk.Frame(root, padding=0)
        btn_frame.pack(side="bottom", pady=0)

        ttk.Button(btn_frame, text="Открыть папку", command=self.open_folder).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Назад", command=self.prev_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Вперёд", command=self.next_image).pack(side="left", padx=5)

        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

        # Автоматическое изменение размера изображения при изменении окна
        self.image_label.bind('<Configure>', self.on_resize)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images = []
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"):
                self.images.extend(glob.glob(os.path.join(folder, ext)))
            self.images.sort()
            self.index = 0
            if self.images:
                self.load_image()
                self.show_image()
            else:
                messagebox.showinfo("Нет изображений", "В выбранной папке нет поддерживаемых изображений.")

    def load_image(self):
        # Загружаем оригинальное изображение и сохраняем его размер
        if not self.images:
            return
        try:
            self.original_image = Image.open(self.images[self.index])
            self.original_size = self.original_image.size
        except Exception as e:
            self.original_image = None
            self.original_size = (0, 0)
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{e}")

    def show_image(self):
        if not self.images or not self.original_image:
            return
        w, h = self.image_label.winfo_width(), self.image_label.winfo_height()
        if w < 100 or h < 100:
            w, h = 800, 600
        # Масштабируем изображение, но не больше оригинального размера
        scale_w = min(w-20, self.original_size[0])
        scale_h = min(h-20, self.original_size[1])
        img = self.original_image.copy()
        img.thumbnail((scale_w, scale_h), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)
        filename = os.path.basename(self.images[self.index])
        self.status_bar.config(
            text=f"{filename}  [{self.index+1} из {len(self.images)}]"
        )
        self.root.title(f"Просмотрщик — {filename}")

    def next_image(self):
        if self.images and self.index < len(self.images) - 1:
            self.index += 1
            self.load_image()
            self.show_image()

    def prev_image(self):
        if self.images and self.index > 0:
            self.index -= 1
            self.load_image()
            self.show_image()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)

    def on_resize(self, event):
        # При изменении размера окна пересчитываем размер изображения
        if self.original_image:
            self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
