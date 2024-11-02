from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import encode  # Библиотека для DataMatrix
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import filedialog, messagebox
from pylibdmtx.pylibdmtx import decode
import pdfplumber
from PIL import Image


# Настройки размера меток
LABEL_WIDTH_MM = 19  # Ширина метки в мм
LABEL_HEIGHT_MM = 29  # Высота метки в мм
QR_SIZE_MM = 18  # Размер DataMatrix кода в мм
MM_TO_PIXELS = 11.8  # Коэффициент перевода из мм в пиксели

# Параметры страницы по умолчанию
DEFAULT_PAGE_WIDTH_MM = 20
DEFAULT_PAGE_HEIGHT_MM = 30


def draw_dashed_border(draw, x0, y0, x1, y1, dash_length=5):
    for i in range(x0, x1, dash_length * 2):
        draw.line([(i, y0), (i + dash_length, y0)], fill="black")
        draw.line([(i, y1), (i + dash_length, y1)], fill="black")
    for i in range(y0, y1, dash_length * 2):
        draw.line([(x0, i), (x0, i + dash_length)], fill="black")
        draw.line([(x1, i), (x1, i + dash_length)], fill="black")


def wrap_text(draw, text, font, max_width):
    """Разбивает текст на строки, чтобы он помещался в указанный max_width."""
    lines = []
    words = text.split()
    current_line = words[0]

    for word in words[1:]:
        # Проверка длины текущей строки с добавлением нового слова
        if draw.textlength(current_line + ' ' + word, font=font) <= max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def transform_code(code_text):
    # Шаг 1: Добавляем символ `` в начало
    modified_code = "\x1D" + code_text

    # Шаг 2: Убираем скобки вокруг "(01)" и "(21)"
    modified_code = modified_code.replace("(01)", "01").replace("(21)", "21")

    # Шаг 4: Отсчитываем 6 символов справа и вставляем `` перед ними
    #if len(modified_code) > 6:
    #    modified_code = modified_code[:-6] + "\x1D" + modified_code[-6:]
    #print(modified_code)
    return modified_code
def generate_label_image(code_text):
    print(code_text)
    img = Image.new('RGB', (int(LABEL_WIDTH_MM * MM_TO_PIXELS), int(LABEL_HEIGHT_MM * MM_TO_PIXELS)), color='white')
    draw = ImageDraw.Draw(img)

    # Генерация DataMatrix кода
    data_matrix = encode(code_text.encode('utf-8'))
    qr_img = Image.frombytes('RGB', (data_matrix.width, data_matrix.height), data_matrix.pixels)
    qr_img = qr_img.resize((int(QR_SIZE_MM * MM_TO_PIXELS), int(QR_SIZE_MM * MM_TO_PIXELS)))
    img.paste(qr_img, (int((LABEL_WIDTH_MM - QR_SIZE_MM) * MM_TO_PIXELS // 2), int(5)))

    # Основной шрифт и параметры текста
    font = ImageFont.truetype("arial.ttf", 21)
    max_text_width = img.width - 10  # Учитываем отступы по бокам

    # Дополнительный шрифт и параметры текста
    font_ext = ImageFont.truetype("arialbd.ttf", 36)
    max_text_width_ext = img.width - 10  # Учитываем отступы по бокам

    # Первая строка текста
    substring_gtin = code_text[3:17]
    lines = wrap_text(draw, substring_gtin, font, max_text_width)
    text_y = int(QR_SIZE_MM * MM_TO_PIXELS + 10)

    #for line in lines:
    text_bbox = draw.textbbox((0, 0), substring_gtin, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (img.width - text_width) // 2
    draw.text((text_x, text_y), substring_gtin, fill="black", font=font)
    text_y += text_bbox[3] - text_bbox[1]

    # Условие для присвоения значения additional_text
    if substring_gtin   == "04650118197152":
         additional_text = "ТР445"
    elif substring_gtin == "04650118193338":
         additional_text = "H230"
    elif substring_gtin == "04650118195424":
         additional_text = "H450"
    elif substring_gtin == "04650118192881":
         additional_text = "P445"
    elif substring_gtin == "04650118197350":
         additional_text = "P660"
    else:
         additional_text = ""  # Можно оставить пустым или установить значение по умолчанию


    # Вторая строка текста (пример дополнительного текста)
    #additional_text = "445"
    #additional_lines = wrap_text(draw, additional_text, font_ext, max_text_width_ext)

    #for line in additional_lines:
    text_bbox = draw.textbbox((0, 0), additional_text, font=font_ext)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (img.width - text_width) // 2
    draw.text((text_x, text_y), additional_text, fill="black", font=font_ext)
    text_y += text_bbox[3] - text_bbox[1]

    # Пунктирная рамка
    draw_dashed_border(draw, 0, 0, int(LABEL_WIDTH_MM * MM_TO_PIXELS) - 1, int(LABEL_HEIGHT_MM * MM_TO_PIXELS) - 1)

    return img


from io import BytesIO
from reportlab.lib.utils import ImageReader


def save_labels_to_pdf(codes, output_pdf_path, page_width_mm, page_height_mm):
    page_width_px = page_width_mm * MM_TO_PIXELS
    page_height_px = page_height_mm * MM_TO_PIXELS

    # Создаем canvas для PDF
    c = canvas.Canvas(output_pdf_path, pagesize=(page_width_px, page_height_px))

    for code_text in codes:
        code_text = transform_code(code_text)

        # Генерируем изображение метки напрямую в PIL без сохранения на диск
        label_img = generate_label_image(code_text)

        # Конвертируем изображение в поток
        img_stream = BytesIO()
        label_img.save(img_stream, format='PNG')
        img_stream.seek(0)  # Сбрасываем указатель потока для использования

        # Преобразуем поток изображения для использования с reportlab
        pil_image = ImageReader(img_stream)

        # Вычисляем центр страницы для размещения метки
        x_position = (page_width_px - LABEL_WIDTH_MM * MM_TO_PIXELS) / 2
        y_position = (page_height_px - LABEL_HEIGHT_MM * MM_TO_PIXELS) / 2

        # Добавляем изображение на страницу PDF
        c.drawImage(pil_image, x_position, y_position,
                    width=LABEL_WIDTH_MM * MM_TO_PIXELS,
                    height=LABEL_HEIGHT_MM * MM_TO_PIXELS)
        c.showPage()  # Создаем новую страницу для каждой метки

    # Сохраняем PDF
    c.save()


def generate_preview_and_save_pdf():
    codes = text_box.get("1.0", "end-1c").strip().split("\n")

    try:
        page_width_mm = float(page_width_entry.get())
        page_height_mm = float(page_height_entry.get())
    except ValueError:
        print("Введите корректные числовые значения для размеров страницы.")
        return

    output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_pdf_path:
        save_labels_to_pdf(codes, output_pdf_path, page_width_mm, page_height_mm)
        print(f"PDF сохранен: {output_pdf_path}")


def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        text_box.insert(tk.END, clipboard_text)
    except tk.TclError:
        print("Буфер обмена пуст или недоступен.")


# Функция для чтения и декодирования DataMatrix кодов из PDF
def read_datamatrix_from_pdf(file_path):
    codes = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Получаем изображение всей страницы
                page_image = page.to_image(resolution=300)
                pil_image = page_image.original  # Извлекаем как PIL изображение

                # Декодируем все DataMatrix коды на странице
                decoded_data = decode(pil_image)
                for data in decoded_data:
                    codes.append(data.data.decode())
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать PDF: {e}")
    return codes

# Обработчик кнопки "Прочитать из файла"
def on_read_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    codes = read_datamatrix_from_pdf(file_path)
    if codes:
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, "\n".join(codes))
    else:
        messagebox.showinfo("Результат", "Не найдено кодов DataMatrix")


# Интерфейс
root = tk.Tk()
root.title("Vasteco GS1 DataMartix Label PDF Generator")

# Поле для ввода кода
text_box = tk.Text(root, width=50, height=10)
text_box.pack()

# Кнопка вставки из буфера обмена
#paste_button = tk.Button(root, text="Вставить из буфера", command=paste_from_clipboard)
#paste_button.pack()

# Кнопка "Прочитать из файла"
read_button = tk.Button(root, text="Прочитать из файла", command=on_read_from_file)
read_button.pack()

# Поля ввода для размеров страницы
tk.Label(root, text="Ширина страницы (мм):").pack()
page_width_entry = tk.Entry(root)
page_width_entry.insert(0, str(DEFAULT_PAGE_WIDTH_MM))
page_width_entry.pack()

tk.Label(root, text="Высота страницы (мм):").pack()
page_height_entry = tk.Entry(root)
page_height_entry.insert(0, str(DEFAULT_PAGE_HEIGHT_MM))
page_height_entry.pack()

# Кнопка для генерации и сохранения PDF
generate_pdf_button = tk.Button(root, text="Сохранить в PDF", command=generate_preview_and_save_pdf)
generate_pdf_button.pack()

root.mainloop()
