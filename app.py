from flask import Flask, render_template, request, send_file
from docx import Document
from datetime import datetime
import os

app = Flask(__name__)

months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

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
        
        # Получаем и форматируем даты
        date_formatted = format_date(request.form.get("date"))
        expiry_formatted = format_date(request.form.get("expiry_date"))
        
        # Валидация дат
        if not date_formatted:
            errors.append("Неверная дата оформления рецепта!")
        if not expiry_formatted:
            errors.append("Неверная дата окончания рецепта!")
        
        # Проверка логики дат
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
        
        # Формируем данные для шаблона
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
        
        docx_path = fill_template(data)
        return send_file(docx_path, as_attachment=True)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)