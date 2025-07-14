import os
import glob
from tkinter import Tk, Label, Button, filedialog
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотрщик изображений")
        self.image_label = Label(root)
        self.image_label.pack()
        self.images = []
        self.index = 0

        Button(root, text="Открыть папку", command=self.open_folder).pack(side="left")
        Button(root, text="Назад", command=self.prev_image).pack(side="left")
        Button(root, text="Вперед", command=self.next_image).pack(side="left")
        Button(root, text="Полноэкранный режим", command=self.toggle_fullscreen).pack(side="left")
        self.fullscreen = False

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images = glob.glob(os.path.join(folder, "*.jpg")) + \
                          glob.glob(os.path.join(folder, "*.png")) + \
                          glob.glob(os.path.join(folder, "*.jpeg")) + \
                          glob.glob(os.path.join(folder, "*.gif"))
            self.images.sort()
            self.index = 0
            self.show_image()

    def show_image(self):
        if self.images:
            image = Image.open(self.images[self.index])
            image.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.root.title(f"Просмотрщик — {os.path.basename(self.images[self.index])}")

    def next_image(self):
        if self.images and self.index < len(self.images) - 1:
            self.index += 1
            self.show_image()

    def prev_image(self):
        if self.images and self.index > 0:
            self.index -= 1
            self.show_image()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

if __name__ == "__main__":
    root = Tk()
    viewer = ImageViewer(root)
    root.mainloop()
