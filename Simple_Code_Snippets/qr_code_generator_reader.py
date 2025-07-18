import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, SquareGradiantColorMask, RadialGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask
import pyzbar.pyzbar as pyzbar
import cv2
import io

class QRCodeGeneratorReader:
    def __init__(self, master):
        self.master = master
        master.title("QR Code Generator and Reader")

        # --- Generation Tab ---
        self.generation_tab = ttk.Notebook(master)
        self.generation_tab.pack(pady=10, padx=10, fill="both", expand=True)

        self.generation_frame = ttk.Frame(self.generation_tab)
        self.generation_tab.add(self.generation_frame, text="Generate QR Code")

        self.generation_type_label = ttk.Label(self.generation_frame, text="Data Type:")
        self.generation_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.generation_type = ttk.Combobox(self.generation_frame, values=["Text", "URL", "Contact Info"])
        self.generation_type.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.generation_type.set("Text")
        self.generation_type.bind("<<ComboboxSelected>>", self.update_generation_fields)

        self.data_label = ttk.Label(self.generation_frame, text="Data:")
        self.data_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.data_entry = tk.Text(self.generation_frame, height=5, width=40)
        self.data_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Contact Info fields (initially hidden)
        self.contact_frame = ttk.Frame(self.generation_frame)
        self.contact_name_label = ttk.Label(self.contact_frame, text="Name:")
        self.contact_name_entry = ttk.Entry(self.contact_frame, width=30)
        self.contact_phone_label = ttk.Label(self.contact_frame, text="Phone:")
        self.contact_phone_entry = ttk.Entry(self.contact_frame, width=30)
        self.contact_email_label = ttk.Label(self.contact_frame, text="Email:")
        self.contact_email_entry = ttk.Entry(self.contact_frame, width=30)

        self.qr_image_label = ttk.Label(self.generation_frame, text="QR Code:")
        self.qr_image_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.qr_image_panel = tk.Label(self.generation_frame)
        self.qr_image_panel.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

        self.generate_button = ttk.Button(self.generation_frame, text="Generate QR Code", command=self.generate_qr_code)
        self.generate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.module_drawer_label = ttk.Label(self.generation_frame, text="Module Drawer:")
        self.module_drawer_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.module_drawer_options = ["Rounded", "Square", "Circle", "Gapped Square"]
        self.module_drawer_combo = ttk.Combobox(self.generation_frame, values=self.module_drawer_options)
        self.module_drawer_combo.set("Square")
        self.module_drawer_combo.grid(row=4, column=1, padx=5, pady=5, sticky="ew")


        self.color_mask_label = ttk.Label(self.generation_frame, text="Color Mask:")
        self.color_mask_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.color_mask_options = ["Solid Fill", "Square Gradient", "Radial Gradient", "Horizontal Gradient", "Vertical Gradient"]
        self.color_mask_combo = ttk.Combobox(self.generation_frame, values=self.color_mask_options)
        self.color_mask_combo.set("Solid Fill")
        self.color_mask_combo.grid(row=5, column=1, padx=5, pady=5, sticky="ew")


        self.fg_color_label = ttk.Label(self.generation_frame, text="Foreground Color:")
        self.fg_color_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.fg_color_entry = ttk.Entry(self.generation_frame, width=10)
        self.fg_color_entry.insert(0, "black")
        self.fg_color_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        self.bg_color_label = ttk.Label(self.generation_frame, text="Background Color:")
        self.bg_color_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.bg_color_entry = ttk.Entry(self.generation_frame, width=10)
        self.bg_color_entry.insert(0, "white")
        self.bg_color_entry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")


        self.logo_label = ttk.Label(self.generation_frame, text="Logo Image:")
        self.logo_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.logo_button = ttk.Button(self.generation_frame, text="Browse", command=self.browse_logo)
        self.logo_button.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        self.logo_path = None

        self.save_button = ttk.Button(self.generation_frame, text="Save QR Code", command=self.save_qr_code)
        self.save_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        # --- Reading Tab ---
        self.reading_tab = ttk.Notebook(master)
        self.reading_tab.pack(pady=10, padx=10, fill="both", expand=True)

        self.reading_frame = ttk.Frame(self.reading_tab)
        self.reading_tab.add(self.reading_frame, text="Read QR Code")

        self.image_label = ttk.Label(self.reading_frame, text="Image:")
        self.image_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.image_panel = tk.Label(self.reading_frame)
        self.image_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.browse_button = ttk.Button(self.reading_frame, text="Browse Image", command=self.browse_image)
        self.browse_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.webcam_button = ttk.Button(self.reading_frame, text="Read from Webcam", command=self.read_from_webcam)
        self.webcam_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.decoded_data_label = ttk.Label(self.reading_frame, text="Decoded Data:")
        self.decoded_data_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.decoded_data_text = tk.Text(self.reading_frame, height=5, width=40)
        self.decoded_data_text.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.decoded_data_text.config(state=tk.DISABLED)


        self.image_path = None

        # Configure grid weights
        self.generation_frame.columnconfigure(1, weight=1)
        self.reading_frame.columnconfigure(1, weight=1)

        self.update_generation_fields()


    def update_generation_fields(self, event=None):
        data_type = self.generation_type.get()
        if data_type == "Contact Info":
            self.contact_frame.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
            self.data_entry.grid_forget()
            self.data_label.config(text="Name:")

            self.contact_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.contact_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.contact_phone_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.contact_phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.contact_email_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.contact_email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        else:
            self.contact_frame.grid_forget()
            self.data_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.data_label.config(text="Data:")
            self.contact_name_label.grid_forget()
            self.contact_name_entry.grid_forget()
            self.contact_phone_label.grid_forget()
            self.contact_phone_entry.grid_forget()
            self.contact_email_label.grid_forget()
            self.contact_email_entry.grid_forget()


    def generate_qr_code(self):
        data_type = self.generation_type.get()
        if data_type == "Text":
            data = self.data_entry.get("1.0", tk.END).strip()
        elif data_type == "URL":
            data = self.data_entry.get("1.0", tk.END).strip()
        elif data_type == "Contact Info":
            name = self.contact_name_entry.get().strip()
            phone = self.contact_phone_entry.get().strip()
            email = self.contact_email_entry.get().strip()
            data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone}\nEMAIL:{email}\nEND:VCARD"
        else:
            messagebox.showerror("Error", "Invalid data type.")
            return

        if not data:
            messagebox.showerror("Error", "Data cannot be empty.")
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            module_drawer_str = self.module_drawer_combo.get()
            if module_drawer_str == "Rounded":
                module_drawer = RoundedModuleDrawer()
            elif module_drawer_str == "Square":
                module_drawer = SquareModuleDrawer()
            elif module_drawer_str == "Circle":
                module_drawer = CircleModuleDrawer()
            elif module_drawer_str == "Gapped Square":
                module_drawer = GappedSquareModuleDrawer()
            else:
                module_drawer = SquareModuleDrawer()


            color_mask_str = self.color_mask_combo.get()
            fg_color = self.fg_color_entry.get()
            bg_color = self.bg_color_entry.get()

            if color_mask_str == "Solid Fill":
                color_mask = SolidFillColorMask(fg_color, bg_color)
            elif color_mask_str == "Square Gradient":
                color_mask = SquareGradiantColorMask(fg_color, bg_color)
            elif color_mask_str == "Radial Gradient":
                color_mask = RadialGradiantColorMask(fg_color, bg_color)
            elif color_mask_str == "Horizontal Gradient":
                color_mask = HorizontalGradiantColorMask(fg_color, bg_color)
            elif color_mask_str == "Vertical Gradient":
                color_mask = VerticalGradiantColorMask(fg_color, bg_color)
            else:
                color_mask = SolidFillColorMask(fg_color, bg_color)


            img = qr.make_image(image_factory=StyledPilImage, module_drawer=module_drawer, color_mask=color_mask)



            if self.logo_path:
                try:
                    logo_img = Image.open(self.logo_path).convert("RGBA")
                    width, height = img.size
                    logo_size = int(min(width, height) * 0.2)
                    logo_img = logo_img.resize((logo_size, logo_size))

                    pos = ((width - logo_size) // 2, (height - logo_size) // 2)
                    img.paste(logo_img, pos, logo_img)  # Ensure transparency is handled
                except Exception as e:
                    messagebox.showerror("Error", f"Error embedding logo: {e}")

            img = img.convert("RGB")

            img = ImageTk.PhotoImage(img)
            self.qr_image_panel.config(image=img)
            self.qr_image_panel.image = img

        except Exception as e:
            messagebox.showerror("Error", f"Error generating QR code: {e}")


    def browse_logo(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select Logo Image",
                                              filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("all files", "*.*")))
        if filename:
            self.logo_path = filename

    def save_qr_code(self):
        if not hasattr(self.qr_image_panel, 'image') or self.qr_image_panel.image is None:
            messagebox.showerror("Error", "No QR code generated yet.")
            return

        filename = filedialog.asksaveasfilename(initialdir=".", title="Save QR Code",
                                              filetypes=(("PNG file", "*.png"), ("JPEG file", "*.jpg"), ("all files", "*.*")),
                                              defaultextension=".png")
        if filename:
            try:
                 pil_img = self.qr_image_panel.image._PhotoImage__photo.image
                 pil_img.save(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Error saving QR code: {e}")

    def browse_image(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select Image",
                                              filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("all files", "*.*")))
        if filename:
            self.image_path = filename
            try:
                img = Image.open(filename)
                img = ImageTk.PhotoImage(img)
                self.image_panel.config(image=img)
                self.image_panel.image = img
                self.decode_qr_code()  # Automatically decode after browsing
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {e}")


    def read_from_webcam(self):
        cap = cv2.VideoCapture(0)  # Use default camera (0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = pyzbar.decode(gray)

            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                self.decoded_data_text.config(state=tk.NORMAL)
                self.decoded_data_text.delete("1.0", tk.END)
                self.decoded_data_text.insert(tk.END, data)
                self.decoded_data_text.config(state=tk.DISABLED)

                # Draw a rectangle around the QR code
                rect_pts = obj.polygon
                if len(rect_pts) == 4:
                    cv2.polylines(frame, [obj.polygon], True, (0, 255, 0), 2)

            cv2.imshow("Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break

        cap.release()
        cv2.destroyAllWindows()



    def decode_qr_code(self):
        if self.image_path:
            try:
                img = Image.open(self.image_path)
                decoded_objects = pyzbar.decode(img)

                if decoded_objects:
                    data = decoded_objects[0].data.decode("utf-8")
                    self.decoded_data_text.config(state=tk.NORMAL)
                    self.decoded_data_text.delete("1.0", tk.END)
                    self.decoded_data_text.insert(tk.END, data)
                    self.decoded_data_text.config(state=tk.DISABLED)
                else:
                    self.decoded_data_text.config(state=tk.NORMAL)
                    self.decoded_data_text.delete("1.0", tk.END)
                    self.decoded_data_text.insert(tk.END, "No QR code found.")
                    self.decoded_data_text.config(state=tk.DISABLED)

            except Exception as e:
                messagebox.showerror("Error", f"Error decoding QR code: {e}")



root = tk.Tk()
app = QRCodeGeneratorReader(root)
root.mainloop()