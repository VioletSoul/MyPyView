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

        self.images = []
        self.index = 0
        self.fullscreen = False

        self.frame = ttk.Frame(root, padding=0, borderwidth=0, relief="flat")
        self.frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.image_label = ttk.Label(
            self.frame,
            anchor="center",
            background="#222",
            borderwidth=0,
            relief="flat"
        )
        self.image_label.pack(fill="both", expand=True, padx=0, pady=0)
        self.image_label.bind("<Double-Button-1>", self.toggle_fullscreen)

        self.status_bar = ttk.Label(
            root,
            text="",
            anchor="w",
            relief="sunken",
            background="#222",
            foreground="#fff"
        )
        self.status_bar.pack(side="bottom", fill="x")

        btn_frame = ttk.Frame(root, padding=0, borderwidth=0, relief="flat")
        btn_frame.pack(side="bottom", pady=0)

        ttk.Button(btn_frame, text="Открыть папку", command=self.open_folder).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Назад", command=self.prev_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Вперёд", command=self.next_image).pack(side="left", padx=5)

        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images = []
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"):
                self.images.extend(glob.glob(os.path.join(folder, ext)))
            self.images.sort()
            self.index = 0
            if self.images:
                self.show_image()
            else:
                messagebox.showinfo("Нет изображений", "В выбранной папке нет поддерживаемых изображений.")

    def show_image(self):
        if not self.images:
            return
        try:
            img = Image.open(self.images[self.index])
            w, h = self.image_label.winfo_width(), self.image_label.winfo_height()
            if w < 100 or h < 100:
                w, h = 800, 600
            img.thumbnail((w-20, h-20))
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo)
            filename = os.path.basename(self.images[self.index])
            self.status_bar.config(
                text=f"{filename}  [{self.index+1} из {len(self.images)}]"
            )
            self.root.title(f"Просмотрщик — {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{e}")

    def next_image(self):
        if self.images and self.index < len(self.images) - 1:
            self.index += 1
            self.show_image()

    def prev_image(self):
        if self.images and self.index > 0:
            self.index -= 1
            self.show_image()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()
