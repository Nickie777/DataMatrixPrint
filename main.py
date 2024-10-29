import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import encode  # Библиотека для DataMatrix
import win32print
import win32ui
from PIL import ImageWin

# Настройки размера меток
LABEL_WIDTH_MM = 19  # Ширина метки в мм
LABEL_HEIGHT_MM = 29  # Высота метки в мм
QR_SIZE_MM = 18  # Размер DataMatrix кода в мм
MM_TO_PIXELS = 11.8  # Коэффициент перевода из мм в пиксели


def generate_label_image(code_text):
    # Создаем изображение для одной метки
    img = Image.new('RGB', (int(LABEL_WIDTH_MM * MM_TO_PIXELS), int(LABEL_HEIGHT_MM * MM_TO_PIXELS)), color='white')

    # Генерация DataMatrix-кода
    data_matrix = encode(code_text.encode('utf-8'))
    qr_img = Image.frombytes('RGB', (data_matrix.width, data_matrix.height), data_matrix.pixels)
    qr_img = qr_img.resize((int(QR_SIZE_MM * MM_TO_PIXELS), int(QR_SIZE_MM * MM_TO_PIXELS)))
    img.paste(qr_img, (int((LABEL_WIDTH_MM - QR_SIZE_MM) * MM_TO_PIXELS // 2),
                       int((LABEL_HEIGHT_MM - QR_SIZE_MM - 5) * MM_TO_PIXELS // 2)))

    # Печать кода под DataMatrix, повернутого на 90 градусов
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 10)  # Замените путь к шрифту, если необходимо
    rotated_text_img = Image.new("RGB", (int(LABEL_HEIGHT_MM * MM_TO_PIXELS), int(5 * MM_TO_PIXELS)), color='white')
    rotated_draw = ImageDraw.Draw(rotated_text_img)
    rotated_draw.text((0, 0), code_text, fill="black", font=font)
    rotated_text_img = rotated_text_img.rotate(90, expand=True)
    img.paste(rotated_text_img, (int((LABEL_WIDTH_MM - 5) * MM_TO_PIXELS), 0))

    return img


def generate_preview_and_print():
    # Получение текста из текстбокса и генерация изображения для каждого кода
    codes = text_box.get("1.0", "end-1c").strip().split("\n")
    label_images = [generate_label_image(code) for code in codes]

    # Создание длинного изображения для всей ленты
    full_img_width = len(label_images) * int(LABEL_WIDTH_MM * MM_TO_PIXELS)
    full_img_height = int(LABEL_HEIGHT_MM * MM_TO_PIXELS)
    full_img = Image.new('RGB', (full_img_width, full_img_height), color='white')

    for i, label in enumerate(label_images):
        full_img.paste(label, (i * int(LABEL_WIDTH_MM * MM_TO_PIXELS), 0))

    # Отображение изображения как предварительный просмотр (или можно сохранить)
    full_img.show()

    # Печать ленты
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(win32print.GetDefaultPrinter())
    hdc.StartDoc("Label Print")
    hdc.StartPage()
    dib = ImageWin.Dib(full_img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, full_img.size[0], full_img.size[1]))
    hdc.EndPage()
    hdc.EndDoc()


# Интерфейс
root = tk.Tk()
root.title("Label Printer")

text_box = tk.Text(root, width=50, height=10)
text_box.pack()

print_button = tk.Button(root, text="Вывести на печать", command=generate_preview_and_print)
print_button.pack()

root.mainloop()
