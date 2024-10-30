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
    # Рисуем пунктирную линию вокруг метки
    for i in range(x0, x1, dash_length * 2):
        draw.line([(i, y0), (i + dash_length, y0)], fill="black")  # Верхняя граница
        draw.line([(i, y1), (i + dash_length, y1)], fill="black")  # Нижняя граница
    for i in range(y0, y1, dash_length * 2):
        draw.line([(x0, i), (x0, i + dash_length)], fill="black")  # Левая граница
        draw.line([(x1, i), (x1, i + dash_length)], fill="black")  # Правая граница


def generate_label_image(code_text):
    # Создаем изображение для одной метки
    img = Image.new('RGB', (int(LABEL_WIDTH_MM * MM_TO_PIXELS), int(LABEL_HEIGHT_MM * MM_TO_PIXELS)), color='white')
    draw = ImageDraw.Draw(img)

    # Генерация DataMatrix-кода
    data_matrix = encode(code_text.encode('utf-8'))
    qr_img = Image.frombytes('RGB', (data_matrix.width, data_matrix.height), data_matrix.pixels)
    qr_img = qr_img.resize((int(QR_SIZE_MM * MM_TO_PIXELS), int(QR_SIZE_MM * MM_TO_PIXELS)))
    img.paste(qr_img, (int((LABEL_WIDTH_MM - QR_SIZE_MM) * MM_TO_PIXELS // 2), int(5)))  # QR-код сверху по центру

    # Добавление текста под QR-кодом
    font = ImageFont.truetype("arial.ttf", 10)  # Замените на путь к шрифту, если необходимо
    text_bbox = draw.textbbox((0, 0), code_text, font=font)  # Получаем координаты ограничивающего прямоугольника
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (img.width - text_width) // 2
    text_y = int(QR_SIZE_MM * MM_TO_PIXELS + 10)  # Под QR-кодом с отступом
    draw.text((text_x, text_y), code_text, fill="black", font=font)

    # Добавляем пунктирную границу вокруг метки
    draw_dashed_border(draw, 0, 0, int(LABEL_WIDTH_MM * MM_TO_PIXELS) - 1, int(LABEL_HEIGHT_MM * MM_TO_PIXELS) - 1)

    return img


def save_labels_to_pdf(codes, output_pdf_path):
    # Настраиваем PDF
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4
    x_offset = 10  # Начальный отступ слева
    y_position = height - LABEL_HEIGHT_MM * MM_TO_PIXELS - 20  # Начальный отступ сверху

    for code_text in codes:
        label_img = generate_label_image(code_text)
        temp_path = "temp_label.png"
        label_img.save(temp_path)

        # Вставляем изображение метки в PDF
        c.drawImage(temp_path, x_offset, y_position, width=LABEL_WIDTH_MM * MM_TO_PIXELS,
                    height=LABEL_HEIGHT_MM * MM_TO_PIXELS)

        x_offset += LABEL_WIDTH_MM * MM_TO_PIXELS + 10  # Отступ между метками

        # Проверка на выход за границы страницы
        if x_offset + LABEL_WIDTH_MM * MM_TO_PIXELS > width:
            x_offset = 10  # Сброс отступа
            y_position -= LABEL_HEIGHT_MM * MM_TO_PIXELS + 20  # Перемещение вниз на новую строку

        # Если место закончится на странице, добавляем новую
        if y_position < 0:
            c.showPage()
            y_position = height - LABEL_HEIGHT_MM * MM_TO_PIXELS - 20

    c.save()

    # Удаляем временное изображение
    if os.path.exists(temp_path):
        os.remove(temp_path)


def generate_preview_and_save_pdf():
    # Получение текста из текстбокса
    codes = text_box.get("1.0", "end-1c").strip().split("\n")

    # Выбор пути для сохранения PDF
    output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_pdf_path:
        save_labels_to_pdf(codes, output_pdf_path)
        print(f"PDF сохранен: {output_pdf_path}")


# Интерфейс
root = tk.Tk()
root.title("Label PDF Generator")

text_box = tk.Text(root, width=50, height=10)
text_box.pack()

generate_pdf_button = tk.Button(root, text="Сохранить в PDF", command=generate_preview_and_save_pdf)
generate_pdf_button.pack()

root.mainloop()
