import shutil
import PyPDF2
from PIL import Image
import pytesseract
import time
import os
#

def extract_pdf_image(pdf_path):
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, "rb"), strict=False)
    except PyPDF2.utils.PdfReadError as e:
        return None
    except FileNotFoundError as e:
        return None

    result = []

    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()
        try:
            if page_obj['/Im0'].get('/Subtype') == "/Image":
                size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
                data = page_obj['/Im0']._data
                if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB':
                    mode = 'RGB'
                else:
                    mode = 'P'

                if page_obj['/Im0']['/Filter'] == '/FlateDecode':
                    file_type = 'png'
                elif page_obj['/Im0']['/Filter'] == '/DCTDecode':
                    file_type = 'jpg'
                elif page_obj['/Im0']['/Filter'] == '/JPXDecode':
                    file_type = 'jp2'
                else:
                    file_type = 'bmp'

                result_strict = {
                    'page': page_num,
                    'size': size,
                    'data': data,
                    'mode': mode,
                    'file_type': file_type,
                }
                result.append(result_strict)
        except Exception as e:
            print(e, pdf_path)    #if page_obj['/Im0'].get('/Subtype') == "/Image":

    return result


def save_pdf_image(file_name, f_path, *pdf_strict):
    if pdf_strict:
        for item in pdf_strict:
            name = f"{file_name}_#_{item['page']}.{item['file_type']}"
            new_path1 = os.path.join(f_path,name)
            new_path2 = os.path.normpath(new_path1)
            # new_path2 = new_path1.replace('\\','/')
            try:
                with open(new_path2, "wb") as image:
                    image.write(item['data'])
            except Exception as e:
                # e = Exception
                print(e)
        return 1
    else:
        return -1

# todo Извлечь номер кассы из поля
def extract_number(file_path):
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = 'заводской (серийный) номер'
    pattern2 = 'заводской номер'
    result = []
    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern2) + 1 or line.lower().find(pattern) + 1:
            eng_text = pytesseract.image_to_string(img_obj, 'eng')
            number = eng_text.split('\n')[idx].split(' ')[-1]
            result.append(number)

    # todo при отсутсвии распознавания вернуть соответсвующее сообщение или error
    return result

# Задача: обойти все файлы из архива https://yadi.sk/d/q5kuiXh0YG9GCQ
# Необходимо найти заводские серийные номера кассовых аппаратов из изображений и страниц PDF файлов.
#
# В конечном результате должна полуичться MongoDb база данных в которой явно и наглядно понятно из какого изначального файла был добыт номер или несколько номеров.
# Так же должна быть коллекция в БД в которой указаны пути к файлам из которых не удалось извлечь номера с указанием страницы если изначально это PDF документ.

if __name__ == '__main__':
    from pymongo import MongoClient
    try:
        conn = MongoClient()
    except:
        print("Could not connect to MongoDB")
    # database
    db = conn.Numberdatabase

    # Файлов: 1 220;
    # папок: 234
    source_folder = "C:\\temp\\СКД_Поверка весов"  #исходная директория с PDF и JPG
    images_folder = "C:\\temp\\_images" #директория для images

    try:
        os.mkdir(images_folder, mode=0o777) #, *, dir_fd=None)
    except FileExistsError:
        None

    source_files_pdf = []
    source_files_img = []
    unprocessed_files = []
    unopened_files = [] #список файлов, что вообще не открылись

    # todo Отсортировать файлы jpg и pdf
    for top, dirs, files in os.walk(source_folder):
        for nm in files:
            if nm.endswith(".jpg"):
                source_files_img.append(os.path.join(top, nm))
            elif nm.endswith(".pdf"):
                source_files_pdf.append(os.path.join(top, nm))
            else:
                None
    # исходные файлы распределены по разным спискам -- произведена сортировка на PDF и JPG
    # соберем все файлы в папку image_path, сконвертировав при этом PDF в JPG

    # todo Извлечь jpg из pdf и сохранить в папке изображений
    # todo необработанные файлы сразу поместим в отдельную коллекцию
    collection = db.FailedPDF  # Created or Switched to collection
    image_path = images_folder #сюда сохраним все исходные JPG и сконвертированные PDF->JPG
    for idx,item in enumerate(source_files_pdf):
        pdf_result = extract_pdf_image(item) #pdf_file_path = 'data_for_parse/8416_4.pdf'  #
        if pdf_result!=None:    #случай, когда файл не открылся вообще
            file_name = os.path.basename(item)
            action = save_pdf_image(file_name, image_path, *pdf_result)
            if action<0:
                unprocessed_files.append(item)
                num_dict = {
                    "file": item,
                    "is_opened": True,
                    "is_saved_to_img": False,
                }
                rec_id1 = collection.insert_one(num_dict)

        else:
            unopened_files.append(item) #не открыается вообще
            num_dict = {
                "file": item,
                "is_opened": False,
                "is_saved_to_img": False,
            }
            rec_id1 = collection.insert_one(num_dict)

    # todo исходные JPG тоже скопируем в папку images_folder
    # for idx, item in enumerate(source_files_img):
    #     file_name = os.path.basename(item)
    #     new_path = os.path.join(images_folder,file_name)
    #     shutil.copy2(item, new_path)

    # todo корректно настроить tesseract
    # 1 - устанавливаем пакет из данной ссылки
    # https://github.com/UB-Mannheim/tesseract/wiki
    # 2 - запускаем EXE C:\Program Files\Tesseract-OCR\tesseract.exe
    # 3 файл rus.traineddata помещаем в папку C:\Program Files\Tesseract-OCR\tessdata

    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # todo сохранить все извлеченные номера в БД MONGO
    collection = db.ExtractedNumbers    #Created or Switched to collection
    for top, dirs, files in os.walk(images_folder):
        for nm in files:
            full_path = os.path.join(top, nm)
            res = extract_number(full_path)
            # print(full_path, res)
            num_dict = {
                "file": full_path,
                "number": res,
                "is_extracted": len(res)>0,
            }

            # Insert Data
            rec_id1 = collection.insert_one(num_dict)

