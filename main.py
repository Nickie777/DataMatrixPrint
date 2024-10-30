import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import encode  # Библиотека для DataMatrix
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Настройки размера меток
LABEL_WIDTH_MM = 19  # Ширина метки в мм
LABEL_HEIGHT_MM = 29  # Высота метки в мм
QR_SIZE_MM = 18  # Размер DataMatrix кода в мм
MM_TO_PIXELS = 11.8  # Коэффициент перевода из мм в пиксели


def draw_dashed_border(draw, x0, y0, x1, y1, dash_length=5):
    for i in range(x0, x1, dash_length * 2):
        draw.line([(i, y0), (i + dash_length, y0)], fill="black")
        draw.line([(i, y1), (i + dash_length, y1)], fill="black")
    for i in range(y0, y1, dash_length * 2):
        draw.line([(x0, i), (x0, i + dash_length)], fill="black")
        draw.line([(x1, i), (x1, i + dash_length)], fill="black")


def generate_label_image(code_text):
    img = Image.new('RGB', (int(LABEL_WIDTH_MM * MM_TO_PIXELS), int(LABEL_HEIGHT_MM * MM_TO_PIXELS)), color='white')
    draw = ImageDraw.Draw(img)

    data_matrix = encode(code_text.encode('utf-8'))
    qr_img = Image.frombytes('RGB', (data_matrix.width, data_matrix.height), data_matrix.pixels)
    qr_img = qr_img.resize((int(QR_SIZE_MM * MM_TO_PIXELS), int(QR_SIZE_MM * MM_TO_PIXELS)))
    img.paste(qr_img, (int((LABEL_WIDTH_MM - QR_SIZE_MM) * MM_TO_PIXELS // 2), int(5)))

    font = ImageFont.truetype("arial.ttf", 10)
    text_bbox = draw.textbbox((0, 0), code_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (img.width - text_width) // 2
    text_y = int(QR_SIZE_MM * MM_TO_PIXELS + 10)
    draw.text((text_x, text_y), code_text, fill="black", font=font)

    draw_dashed_border(draw, 0, 0, int(LABEL_WIDTH_MM * MM_TO_PIXELS) - 1, int(LABEL_HEIGHT_MM * MM_TO_PIXELS) - 1)

    return img


def save_labels_to_pdf(codes, output_pdf_path):
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4
    x_offset = 10
    y_position = height - LABEL_HEIGHT_MM * MM_TO_PIXELS - 20

    for code_text in codes:
        label_img = generate_label_image(code_text)
        temp_path = "temp_label.png"
        label_img.save(temp_path)

        c.drawImage(temp_path, x_offset, y_position, width=LABEL_WIDTH_MM * MM_TO_PIXELS,
                    height=LABEL_HEIGHT_MM * MM_TO_PIXELS)

        x_offset += LABEL_WIDTH_MM * MM_TO_PIXELS + 10

        if x_offset + LABEL_WIDTH_MM * MM_TO_PIXELS > width:
            x_offset = 10
            y_position -= LABEL_HEIGHT_MM * MM_TO_PIXELS + 20

        if y_position < 0:
            c.showPage()
            y_position = height - LABEL_HEIGHT_MM * MM_TO_PIXELS - 20

    c.save()

    if os.path.exists(temp_path):
        os.remove(temp_path)


def generate_preview_and_save_pdf():
    codes = text_box.get("1.0", "end-1c").strip().split("\n")

    output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_pdf_path:
        save_labels_to_pdf(codes, output_pdf_path)
        print(f"PDF сохранен: {output_pdf_path}")


def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        text_box.insert(tk.END, clipboard_text)
    except tk.TclError:
        print("Буфер обмена пуст или недоступен.")


# Интерфейс
root = tk.Tk()
root.title("Label PDF Generator")

text_box = tk.Text(root, width=50, height=10)
text_box.pack()

paste_button = tk.Button(root, text="Вставить из буфера", command=paste_from_clipboard)
paste_button.pack()

generate_pdf_button = tk.Button(root, text="Сохранить в PDF", command=generate_preview_and_save_pdf)
generate_pdf_button.pack()

root.mainloop()
