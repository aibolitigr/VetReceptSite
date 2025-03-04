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

def fill_template(data, filename):
    os.makedirs("temp", exist_ok=True)
    template_path = "template.docx"
    output_path = os.path.join("temp", filename)
    
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if key in paragraph.text:
                for run in paragraph.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
                        run.bold = True
                        run.underline = True
    
    doc.save(output_path)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        errors = []
        form_data = request.form.to_dict()
        
        date_formatted = format_date(form_data.get("date"))
        expiry_formatted = format_date(form_data.get("expiry_date"))
        
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
        
        owner = form_data.get("owner_name", "").strip()
        pet = form_data.get("pet_info", "").strip()
        surname = owner.split()[0] if owner else "Без_фамилии"
        pet_name = pet.split(',')[0].strip() if ',' in pet else pet.split()[0] if pet else "Без_клички"
        filename = f"{sanitize_filename(surname)}_{sanitize_filename(pet_name)}.docx"
        
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
        
        docx_path = fill_template(data, filename)
        response = send_file(docx_path, as_attachment=True, download_name=filename)
        
        @response.call_on_close
        def delete_file():
            try:
                os.remove(docx_path)
            except Exception as e:
                app.logger.error(f"Ошибка удаления: {e}")
        
        return response
    
    return render_template('form.html')

if __name__ == '__main__':
    if not os.path.exists("temp"):
        os.makedirs("temp")
    app.run(host='0.0.0.0', port=5000, debug=False)