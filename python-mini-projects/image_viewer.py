import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_image():
    filepath = filedialog.askopenfilename(
        initialdir=".", title="Select an image", filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
    )
    if filepath:
        try:
            img = Image.open(filepath)
            img.thumbnail((800, 600))  # Resize image if it's too large
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            label.config(text=f"Error opening image: {e}")

root = tk.Tk()
root.title("Simple Image Viewer")

button = tk.Button(root, text="Open Image", command=open_image)
button.pack(pady=10)

label = tk.Label(root)
label.pack()

root.mainloop()
