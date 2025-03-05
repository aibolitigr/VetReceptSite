from flask import Flask, render_template, request, send_file
from docx import Document
from datetime import datetime
import os
import re

app = Flask(__name__)

months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name).strip().replace(' ', '_')

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {months_ru[date_obj.month]} {date_obj.year} г."
    except (ValueError, KeyError):
        return None

def fill_template(data):
    template_path = "template.docx"
    output_path = "filled_recipe.docx"
    
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
        form_data = request.form.to_dict()
        
        # Валидация дат
        date_formatted = format_date(form_data.get("date"))
        expiry_formatted = format_date(form_data.get("expiry_date"))
        
        # Проверка ошибок
        if not date_formatted:
            errors.append("Неверная дата оформления!")
        if not expiry_formatted:
            errors.append("Неверная дата окончания!")
        
        if date_formatted and expiry_formatted:
            try:
                date_obj = datetime.strptime(form_data.get("date"), "%Y-%m-%d")
                expiry_obj = datetime.strptime(form_data.get("expiry_date"), "%Y-%m-%d")
                if expiry_obj < date_obj:
                    errors.append("Дата окончания не может быть раньше оформления!")
            except ValueError:
                pass
        
        if errors:
            return render_template('form.html', errors=errors, form_data=form_data)
        
        # Формирование данных для шаблона
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
        return send_file(docx_path, as_attachment=True)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)