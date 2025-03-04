from flask import Flask, render_template, request, send_file
from docx import Document
from datetime import datetime
import os
import re

app = Flask(__name__)

# Словарь русских месяцев
months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def sanitize_filename(name):
    """Очистка имени от недопустимых символов"""
    return re.sub(r'[\\/*?:"<>|]', '', name).strip().replace(' ', '_')

def format_date(date_str):
    """Форматирование даты в русский формат"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {months_ru[date_obj.month]} {date_obj.year} г."
    except (ValueError, KeyError):
        return None

def fill_template(data, filename):
    template_path = "template.docx"
    
    # Создаём папку temp, если её нет
    os.makedirs("temp", exist_ok=True)
    
    output_path = os.path.join("temp", filename)
    
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, value)
    
    doc.save(output_path)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        errors = []
        
        # Проверка и форматирование дат
        date_formatted = format_date(request.form.get("date"))
        expiry_formatted = format_date(request.form.get("expiry_date"))
        
        # Валидация
        if not date_formatted:
            errors.append("Неверная дата оформления рецепта!")
        if not expiry_formatted:
            errors.append("Неверная дата окончания рецепта!")
        
        if date_formatted and expiry_formatted:
            try:
                date_obj = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
                expiry_obj = datetime.strptime(request.form.get("expiry_date"), "%Y-%m-%d")
                if expiry_obj < date_obj:
                    errors.append("Дата окончания не может быть раньше даты оформления!")
            except ValueError:
                pass
        
        if errors:
            return "<br>".join(errors) + "<br><br><a href='/'>Вернуться к форме</a>"
        
        # Генерация имени файла
        owner = request.form.get("owner_name", "").strip()
        pet = request.form.get("pet_info", "").strip()

        # Извлекаем фамилию (первое слово)
        surname = owner.split()[0] if owner else "Без_фамилии"

        # Извлекаем кличку (первое слово до запятой или первое слово)
        if ',' in pet:
         pet_name = pet.split(',')[0].strip()
        elif ' ' in pet:
         pet_name = pet.split()[0].strip()
        else:
         pet_name = pet if pet else "Без_клички"

        # Очистка от спецсимволов
        surname_clean = re.sub(r'[\\/*?:"<>|]', '', surname).replace(' ', '_')
        pet_clean = re.sub(r'[\\/*?:"<>|]', '', pet_name).replace(' ', '_')

        filename = f"{surname_clean}_{pet_clean}.docx"        
        # Заполнение данных
        data = {
            "{instance_number}": request.form.get("instance_number"),
            "{recipe_number}": request.form.get("recipe_number"),
            "{date}": date_formatted,
            "{owner_name}": request.form.get("owner_name"),
            "{pet_info}": request.form.get("pet_info"),
            "{medicine}": request.form.get("medicine"),
            "{dosage}": request.form.get("dosage"),
            "{single_dose}": request.form.get("single_dose"),
            "{frequency}": request.form.get("frequency"),
            "{time_of_day}": request.form.get("time_of_day"),
            "{duration}": request.form.get("duration"),
            "{method}": request.form.get("method"),
            "{feeding_time}": request.form.get("feeding_time"),
            "{vet_name}": request.form.get("vet_name"),
            "{expiry_date}": expiry_formatted
        }
        
        # Создание и отправка файла
        docx_path = fill_template(data, filename)
        response = send_file(docx_path, as_attachment=True, download_name=filename)
        
        # Автоудаление временного файла
        @response.call_on_close
        def delete_file():
            try:
                os.remove(docx_path)
            except Exception as e:
                app.logger.error(f"Ошибка удаления файла: {e}")
        
        return response
    
    return render_template('form.html')

if __name__ == '__main__':
    if not os.path.exists("temp"):
        os.makedirs("temp")
    app.run(host='0.0.0.0', port=5000, debug=True)