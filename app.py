from flask import Flask, render_template, request, send_file
from docx import Document
from datetime import datetime
import os
import re
import logging
import time

app = Flask(__name__)

# Настройка логирования
app.logger.setLevel(logging.DEBUG)

# Установка часового пояса
os.environ['TZ'] = 'Europe/Moscow'
try:
    time.tzset()
except AttributeError:
    pass  # Для Windows это не требуется

months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def sanitize_filename(name):
    clean_name = re.sub(r'[\\/*?:"<>|]', '', name)
    clean_name = clean_name.strip().replace(' ', '_')
    return clean_name if clean_name else "unnamed"

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {months_ru[date_obj.month]} {date_obj.year} г."
    except (ValueError, KeyError):
        return None

def fill_template(data):
    template_path = "template.docx"
    output_path = "/tmp/filled_recipe.docx"  # Для Render
    
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, str(value))
    
    doc.save(output_path)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        errors = []
        form_data = request.form.to_dict()
        
        # Проверка обязательных полей
        required_fields = [
            'date', 'expiry_date', 'owner_name', 'pet_info',
            'medicine', 'dosage', 'single_dose', 'frequency',
            'time_of_day', 'duration', 'method', 'feeding_time', 'vet_name'
        ]
        
        for field in required_fields:
            if not form_data.get(field):
                errors.append(f"Поле {field.replace('_', ' ')} обязательно для заполнения!")

        # Обработка дат
        date_str = form_data.get("date")
        expiry_str = form_data.get("expiry_date")
        
        date_formatted = format_date(date_str) if date_str else None
        expiry_formatted = format_date(expiry_str) if expiry_str else None
        
        if date_str and not date_formatted:
            errors.append("Неверный формат даты оформления!")
        if expiry_str and not expiry_formatted:
            errors.append("Неверный формат даты окончания!")
        
        # Сравнение дат
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str else None
            expiry_obj = datetime.strptime(expiry_str, "%Y-%m-%d") if expiry_str else None
            if date_obj and expiry_obj and expiry_obj < date_obj:
                errors.append("Дата окончания не может быть раньше оформления!")
        except ValueError:
            pass
        
        if errors:
            return render_template('form.html', errors=errors, form_data=form_data)
        
                # Формирование имени файла (только фамилия и дата)
        owner = form_data.get("owner_name", "").strip()
        
        # Извлечение фамилии
        surname_parts = owner.split()
        surname = sanitize_filename(surname_parts[0]) if surname_parts else "Без_фамилии"
        
        # Проверка фамилии
        if not surname or surname == "Без_фамилии":
            errors.append("Фамилия владельца обязательна!")
        
        # Формат даты: DD-MM-YYYY
        current_date = datetime.now().strftime("%d-%m-%Y")
        filename = f"{surname}_{current_date}.docx"
        
        # Логирование
        app.logger.debug(f"Generated filename: {filename}")
        app.logger.debug(f"Owner: {owner} → Surname: {surname}")  # Только это!

        # Данные для замены
        data = {
            "{date}": date_formatted,
            "{owner_name}": form_data.get("owner_name"),
            "{pet_info}": form_data.get("pet_info"),
            "{medicine}": form_data.get("medicine"),
            "{dosage}": form_data.get("dosage"),
            "{single_dose}": form_data.get("single_dose"),
            "{frequency}": form_data.get("frequency"),
            "{time_of_day}": form_data.get("time_of_day"),
            "{duration}": form_data.get("duration"),
            "{method}": form_data.get("method"),
            "{feeding_time}": form_data.get("feeding_time"),
            "{vet_name}": form_data.get("vet_name"),
            "{expiry_date}": expiry_formatted
        }
        
        docx_path = fill_template(data)
        return send_file(docx_path, as_attachment=True, download_name=filename)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)