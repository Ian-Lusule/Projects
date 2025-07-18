import os
import sys
import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import LTImage
import fitz  # PyMuPDF
import pytesseract
from wand.image import Image as WandImage
from pathlib import Path
import re
import datetime

class PDFManipulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced PDF Manipulator")
        self.pdf_files = []
        self.output_path = ""
        self.setup_ui()

    def setup_ui(self):
        # Notebook for different operations
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Tabs
        self.create_merge_tab()
        self.create_split_tab()
        self.create_rotate_tab()
        self.create_watermark_tab()
        self.create_encrypt_decrypt_tab()
        self.create_extract_tab()
        self.create_convert_tab()
        self.create_create_tab()
        self.create_form_tab()

        # Common Components
        self.create_browse_button()
        self.create_output_path_selection()

    def create_browse_button(self):
        browse_frame = ttk.Frame(self.root)
        browse_frame.pack(pady=5)

        browse_button = ttk.Button(browse_frame, text="Add PDF Files", command=self.browse_files)
        browse_button.pack(side=tk.LEFT, padx=5)

        self.file_listbox = tk.Listbox(browse_frame, width=60, height=5)
        self.file_listbox.pack(side=tk.LEFT, padx=5)

        remove_button = ttk.Button(browse_frame, text="Remove Selected", command=self.remove_selected_files)
        remove_button.pack(side=tk.LEFT, padx=5)

    def remove_selected_files(self):
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            for index in reversed(selected_indices):
                del self.pdf_files[index]
                self.file_listbox.delete(index)

    def browse_files(self):
        filenames = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for filename in filenames:
            if filename not in self.pdf_files:
                self.pdf_files.append(filename)
                self.file_listbox.insert(tk.END, filename)

    def create_output_path_selection(self):
        output_frame = ttk.Frame(self.root)
        output_frame.pack(pady=5)

        output_label = ttk.Label(output_frame, text="Output Path:")
        output_label.pack(side=tk.LEFT, padx=5)

        self.output_path_entry = ttk.Entry(output_frame, width=50)
        self.output_path_entry.pack(side=tk.LEFT, padx=5)

        output_browse_button = ttk.Button(output_frame, text="Browse", command=self.browse_output_path)
        output_browse_button.pack(side=tk.LEFT, padx=5)

    def browse_output_path(self):
        self.output_path = filedialog.askdirectory()
        self.output_path_entry.insert(0, self.output_path)

    def create_merge_tab(self):
        merge_tab = ttk.Frame(self.notebook)
        self.notebook.add(merge_tab, text="Merge PDFs")

        merge_button = ttk.Button(merge_tab, text="Merge PDFs", command=self.merge_pdfs)
        merge_button.pack(pady=20)

    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF files selected for merging.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            merger = PyPDF2.PdfMerger()
            for pdf_file in self.pdf_files:
                merger.append(pdf_file)

            output_filename = os.path.join(self.output_path, "merged.pdf")
            merger.write(output_filename)
            merger.close()

            messagebox.showinfo("Success", f"PDFs merged successfully to {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error merging PDFs: {e}")

    def create_split_tab(self):
        split_tab = ttk.Frame(self.notebook)
        self.notebook.add(split_tab, text="Split PDFs")

        split_label = ttk.Label(split_tab, text="Split After Page:")
        split_label.pack(pady=5)

        self.split_page_entry = ttk.Entry(split_tab, width=10)
        self.split_page_entry.pack(pady=5)

        split_button = ttk.Button(split_tab, text="Split PDF", command=self.split_pdf)
        split_button.pack(pady=20)

    def split_pdf(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for splitting.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for splitting")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            split_page = int(self.split_page_entry.get())
            pdf_file = self.pdf_files[0]
            reader = PyPDF2.PdfReader(pdf_file)

            if split_page >= len(reader.pages):
                messagebox.showerror("Error", "Split page number is out of range.")
                return

            output_filename1 = os.path.join(self.output_path, "split_part1.pdf")
            output_filename2 = os.path.join(self.output_path, "split_part2.pdf")

            writer1 = PyPDF2.PdfWriter()
            writer2 = PyPDF2.PdfWriter()

            for i in range(split_page):
                writer1.add_page(reader.pages[i])

            for i in range(split_page, len(reader.pages)):
                writer2.add_page(reader.pages[i])

            with open(output_filename1, "wb") as f:
                writer1.write(f)
            with open(output_filename2, "wb") as f:
                writer2.write(f)

            messagebox.showinfo("Success", f"PDF split successfully into {output_filename1} and {output_filename2}")

        except ValueError:
            messagebox.showerror("Error", "Invalid split page number.")
        except Exception as e:
            messagebox.showerror("Error", f"Error splitting PDF: {e}")

    def create_rotate_tab(self):
        rotate_tab = ttk.Frame(self.notebook)
        self.notebook.add(rotate_tab, text="Rotate Pages")

        rotate_label = ttk.Label(rotate_tab, text="Rotation Angle (degrees):")
        rotate_label.pack(pady=5)

        self.rotate_angle_entry = ttk.Entry(rotate_tab, width=10)
        self.rotate_angle_entry.insert(0, "90")
        self.rotate_angle_entry.pack(pady=5)

        rotate_button = ttk.Button(rotate_tab, text="Rotate Pages", command=self.rotate_pages)
        rotate_button.pack(pady=20)

    def rotate_pages(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for rotation.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for rotation")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            rotation_angle = int(self.rotate_angle_entry.get())
            pdf_file = self.pdf_files[0]
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                page.rotate(rotation_angle)
                writer.add_page(page)

            output_filename = os.path.join(self.output_path, "rotated.pdf")
            with open(output_filename, "wb") as f:
                writer.write(f)

            messagebox.showinfo("Success", f"Pages rotated successfully to {output_filename}")

        except ValueError:
            messagebox.showerror("Error", "Invalid rotation angle.")
        except Exception as e:
            messagebox.showerror("Error", f"Error rotating pages: {e}")

    def create_watermark_tab(self):
        watermark_tab = ttk.Frame(self.notebook)
        self.notebook.add(watermark_tab, text="Add Watermark")

        watermark_type_label = ttk.Label(watermark_tab, text="Watermark Type:")
        watermark_type_label.pack(pady=5)

        self.watermark_type = tk.StringVar(value="text")
        text_radio = ttk.Radiobutton(watermark_tab, text="Text", variable=self.watermark_type, value="text")
        image_radio = ttk.Radiobutton(watermark_tab, text="Image", variable=self.watermark_type, value="image")
        text_radio.pack(pady=2, anchor=tk.W)
        image_radio.pack(pady=2, anchor=tk.W)

        self.text_watermark_frame = ttk.Frame(watermark_tab)
        self.image_watermark_frame = ttk.Frame(watermark_tab)

        # Text Watermark
        text_watermark_label = ttk.Label(self.text_watermark_frame, text="Watermark Text:")
        text_watermark_label.pack(pady=2)

        self.watermark_text_entry = ttk.Entry(self.text_watermark_frame, width=30)
        self.watermark_text_entry.pack(pady=2)

        # Image Watermark
        image_watermark_label = ttk.Label(self.image_watermark_frame, text="Watermark Image:")
        image_watermark_label.pack(pady=2)

        self.watermark_image_path = tk.StringVar()
        self.watermark_image_entry = ttk.Entry(self.image_watermark_frame, textvariable=self.watermark_image_path, width=30)
        self.watermark_image_entry.pack(side=tk.LEFT, padx=2)

        image_browse_button = ttk.Button(self.image_watermark_frame, text="Browse Image", command=self.browse_watermark_image)
        image_browse_button.pack(side=tk.LEFT, padx=2)

        self.show_watermark_options()

        watermark_button = ttk.Button(watermark_tab, text="Add Watermark", command=self.add_watermark)
        watermark_button.pack(pady=20)

    def browse_watermark_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        self.watermark_image_path.set(filename)

    def show_watermark_options(self):
        if self.watermark_type.get() == "text":
            self.text_watermark_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.image_watermark_frame.pack_forget()
        else:
            self.image_watermark_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.text_watermark_frame.pack_forget()

    def add_watermark(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            pdf_file = self.pdf_files[0]
            output_filename = os.path.join(self.output_path, "watermarked.pdf")
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()

            if self.watermark_type.get() == "text":
                watermark_text = self.watermark_text_entry.get()
                if not watermark_text:
                    messagebox.showerror("Error", "Please enter watermark text.")
                    return

                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont('Helvetica', 60)
                can.setFillColor(HexColor("#AAAAAA"))
                can.saveState()
                can.translate(letter[0]/2, letter[1]/2)
                can.rotate(45)
                can.drawCentredString(0, 0, watermark_text)
                can.restoreState()
                can.save()
                packet.seek(0)

                watermark = PyPDF2.PdfReader(packet).pages[0]
            else:  # Image Watermark
                image_path = self.watermark_image_path.get()
                if not image_path or not os.path.exists(image_path):
                    messagebox.showerror("Error", "Invalid watermark image path.")
                    return

                img = Image.open(image_path)
                img_width, img_height = img.size
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.drawImage(image_path, letter[0]/2 - img_width/2, letter[1]/2 - img_height/2, width=img_width, height=img_height)
                can.save()
                packet.seek(0)
                watermark = PyPDF2.PdfReader(packet).pages[0]

            for page in reader.pages:
                page.merge_page(watermark)
                writer.add_page(page)

            with open(output_filename, "wb") as f:
                writer.write(f)

            messagebox.showinfo("Success", f"Watermark added successfully to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding watermark: {e}")

    def create_encrypt_decrypt_tab(self):
        encrypt_decrypt_tab = ttk.Frame(self.notebook)
        self.notebook.add(encrypt_decrypt_tab, text="Encrypt/Decrypt")

        password_label = ttk.Label(encrypt_decrypt_tab, text="Password:")
        password_label.pack(pady=5)

        self.password_entry = ttk.Entry(encrypt_decrypt_tab, width=20, show="*")
        self.password_entry.pack(pady=5)

        encrypt_button = ttk.Button(encrypt_decrypt_tab, text="Encrypt PDF", command=self.encrypt_pdf)
        encrypt_button.pack(pady=10)

        decrypt_button = ttk.Button(encrypt_decrypt_tab, text="Decrypt PDF", command=self.decrypt_pdf)
        decrypt_button.pack(pady=10)

    def encrypt_pdf(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for encryption.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for encryption.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            password = self.password_entry.get()
            if not password:
                messagebox.showerror("Error", "Please enter a password for encryption.")
                return

            pdf_file = self.pdf_files[0]
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)
            output_filename = os.path.join(self.output_path, "encrypted.pdf")

            with open(output_filename, "wb") as f:
                writer.write(f)

            messagebox.showinfo("Success", f"PDF encrypted successfully to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error encrypting PDF: {e}")

    def decrypt_pdf(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for decryption.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for decryption.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            password = self.password_entry.get()
            if not password:
                messagebox.showerror("Error", "Please enter the password for decryption.")
                return

            pdf_file = self.pdf_files[0]
            reader = PyPDF2.PdfReader(pdf_file)

            if not reader.is_encrypted:
                messagebox.showinfo("Info", "PDF is not encrypted.")
                return

            if not reader.decrypt(password):
                messagebox.showerror("Error", "Incorrect password for decryption.")
                return

            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            output_filename = os.path.join(self.output_path, "decrypted.pdf")
            with open(output_filename, "wb") as f:
                writer.write(f)

            messagebox.showinfo("Success", f"PDF decrypted successfully to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error decrypting PDF: {e}")

    def create_extract_tab(self):
        extract_tab = ttk.Frame(self.notebook)
        self.notebook.add(extract_tab, text="Extract Content")

        extract_type_label = ttk.Label(extract_tab, text="Extract Type:")
        extract_type_label.pack(pady=5)

        self.extract_type = tk.StringVar(value="text")
        text_radio = ttk.Radiobutton(extract_tab, text="Text", variable=self.extract_type, value="text")
        image_radio = ttk.Radiobutton(extract_tab, text="Images", variable=self.extract_type, value="images")
        ocr_radio = ttk.Radiobutton(extract_tab, text="OCR (Text from Images)", variable=self.extract_type, value="ocr")
        text_radio.pack(pady=2, anchor=tk.W)
        image_radio.pack(pady=2, anchor=tk.W)
        ocr_radio.pack(pady=2, anchor=tk.W)

        extract_button = ttk.Button(extract_tab, text="Extract", command=self.extract_content)
        extract_button.pack(pady=20)

    def extract_content(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for extraction.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for extraction.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            pdf_file = self.pdf_files[0]
            extract_type = self.extract_type.get()

            if extract_type == "text":
                self.extract_text(pdf_file)
            elif extract_type == "images":
                self.extract_images(pdf_file)
            elif extract_type == "ocr":
                self.extract_text_with_ocr(pdf_file)

        except Exception as e:
            messagebox.showerror("Error", f"Error extracting content: {e}")

    def extract_text(self, pdf_file):
        try:
            text = extract_text(pdf_file)
            output_filename = os.path.join(self.output_path, "extracted_text.txt")
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Success", f"Text extracted successfully to {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting text: {e}")

    def extract_images(self, pdf_file):
        try:
            doc = fitz.open(pdf_file)  # PyMuPDF
            image_dir = os.path.join(self.output_path, "extracted_images")
            os.makedirs(image_dir, exist_ok=True)

            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_filename = os.path.join(image_dir, f"page_{page_index + 1}_image_{img_index + 1}.{image_ext}")

                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)

            messagebox.showinfo("Success", f"Images extracted successfully to {image_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting images: {e}")

    def extract_text_with_ocr(self, pdf_file):
        try:
            doc = fitz.open(pdf_file)
            full_text = ""

            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                full_text += text

            output_filename = os.path.join(self.output_path, "ocr_extracted_text.txt")
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(full_text)

            messagebox.showinfo("Success", f"Text extracted with OCR successfully to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error extracting text with OCR: {e}")

    def create_convert_tab(self):
        convert_tab = ttk.Frame(self.notebook)
        self.notebook.add(convert_tab, text="Convert PDF")

        convert_type_label = ttk.Label(convert_tab, text="Convert To:")
        convert_type_label.pack(pady=5)

        self.convert_type = tk.StringVar(value="text")
        text_radio = ttk.Radiobutton(convert_tab, text="Text", variable=self.convert_type, value="text")
        image_radio = ttk.Radiobutton(convert_tab, text="Images", variable=self.convert_type, value="images")
        text_radio.pack(pady=2, anchor=tk.W)
        image_radio.pack(pady=2, anchor=tk.W)

        convert_button = ttk.Button(convert_tab, text="Convert", command=self.convert_pdf)
        convert_button.pack(pady=20)

    def convert_pdf(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF file selected for conversion.")
            return

        if len(self.pdf_files) > 1:
            messagebox.showerror("Error", "Please select only one PDF for conversion.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            pdf_file = self.pdf_files[0]
            convert_type = self.convert_type.get()

            if convert_type == "text":
                self.convert_to_text(pdf_file)
            elif convert_type == "images":
                self.convert_to_images(pdf_file)

        except Exception as e:
            messagebox.showerror("Error", f"Error converting PDF: {e}")

    def convert_to_text(self, pdf_file):
        try:
            text = extract_text(pdf_file)
            output_filename = os.path.join(self.output_path, "converted_text.txt")
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Success", f"PDF converted to text successfully to {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error converting PDF to text: {e}")

    def convert_to_images(self, pdf_file):
        try:
            doc = fitz.open(pdf_file)
            image_dir = os.path.join(self.output_path, "converted_images")
            os.makedirs(image_dir, exist_ok=True)

            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                pix = page.get_pixmap()
                image_filename = os.path.join(image_dir, f"page_{page_index + 1}.png")
                pix.save(image_filename)
            messagebox.showinfo("Success", f"PDF converted to images successfully to {image_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Error converting PDF to images: {e}")

    def create_create_tab(self):
        create_tab = ttk.Frame(self.notebook)
        self.notebook.add(create_tab, text="Create PDF")

        text_label = ttk.Label(create_tab, text="Text to add to PDF:")
        text_label.pack(pady=5)

        self.pdf_text_entry = tk.Text(create_tab, width=40, height=10)
        self.pdf_text_entry.pack(pady=5)

        create_button = ttk.Button(create_tab, text="Create PDF", command=self.create_pdf)
        create_button.pack(pady=20)

    def create_pdf(self):
        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            pdf_text = self.pdf_text_entry.get("1.0", tk.END)
            output_filename = os.path.join(self.output_path, "created.pdf")
            c = canvas.Canvas(output_filename, pagesize=letter)
            textobject = c.beginText()
            textobject.setTextOrigin(inch, 11*inch)
            textobject.setFont('Helvetica', 12)

            for line in pdf_text.splitlines():
                textobject.textLine(line)

            c.drawText(textobject)
            c.save()

            messagebox.showinfo("Success", f"PDF created successfully to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error creating PDF: {e}")

    def create_form_tab(self):
        form_tab = ttk.Frame(self.notebook)
        self.notebook.add(form_tab, text="Fill PDF Form")

        form_label = ttk.Label(form_tab, text="PDF Form File:")
        form_label.pack(pady=5)

        self.form_file_path = tk.StringVar()
        self.form_file_entry = ttk.Entry(form_tab, textvariable=self.form_file_path, width=40)
        self.form_file_entry.pack(side=tk.LEFT, padx=2)

        form_browse_button = ttk.Button(form_tab, text="Browse Form", command=self.browse_form_file)
        form_browse_button.pack(side=tk.LEFT, padx=2)

        fill_button = ttk.Button(form_tab, text="Fill Form", command=self.fill_form)
        fill_button.pack(pady=20)

    def browse_form_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.form_file_path.set(filename)

    def fill_form(self):
        form_pdf = self.form_file_path.get()
        if not form_pdf:
            messagebox.showerror("Error", "Please select a PDF form file.")
            return

        if not os.path.exists(form_pdf):
            messagebox.showerror("Error", "Form PDF file not found.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "No output path selected.")
            return

        try:
            pdf = fitz.open(form_pdf)
            form_fields = {}
            for page in pdf:
                widgets = page.widgets()
                for widget in widgets:
                    form_fields[widget.field_name] = ""

            # Open dialog to get field values
            values = self.get_form_values(form_fields)
            if values is None:
                return  # User cancelled the dialog

            for page in pdf:
                widgets = page.widgets()
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name in values:
                        widget.set_text(str(values[field_name]))

            output_filename = os.path.join(self.output_path, "form_filled.pdf")
            pdf.save(output_filename)
            pdf.close()

            messagebox.showinfo("Success", f"Form filled successfully and saved to {output_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error filling form: {e}")

    def get_form_values(self, fields):
        dialog = FormInputDialog(self.root, fields)
        return dialog.result

class FormInputDialog(simpledialog.Dialog):
    def __init__(self, parent, fields):
        self.fields = fields
        self.result = None
        super().__init__(parent, "Fill PDF Form Fields")

    def body(self, master):
        self.entries = {}
        row = 0
        for field, value in self.fields.items():
            label = ttk.Label(master, text=field + ":")
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(master, width=40)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, sticky=tk.E, padx=5, pady=5)
            self.entries[field] = entry
            row += 1

        return self.entries[list(self.entries.keys())[0]] # initial focus

    def apply(self):
        self.result = {}
        for field, entry in self.entries.items():
            self.result[field] = entry.get()


if __name__ == "__main__":
    root = tk.Tk()
    gui = PDFManipulatorGUI(root)
    root.mainloop()