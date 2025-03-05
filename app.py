from flask import Flask, render_template, request, send_file
from docx import Document
from datetime import datetime
import os
import re
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

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
    except (ValueError, KeyError) as e:
        app.logger.error(f"Ошибка даты: {str(e)}")
        return None

def fill_template(data, filename):
    try:
        template_path = "template.docx"
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Файл {template_path} не найден!")
        
        app.logger.info(f"Открытие шаблона: {os.path.abspath(template_path)}")
        doc = Document(template_path)
        
        # Логирование структуры документа
        app.logger.info("Структура шаблона:")
        for i, paragraph in enumerate(doc.paragraphs):
            app.logger.info(f"[Параграф {i}] {paragraph.text[:50]}...")

        # Замена плейсхолдеров
        replaced = False
        for paragraph in doc.paragraphs:
            for key, value in data.items():
                if key in paragraph.text:
                    app.logger.info(f"Найдено совпадение: {key} -> {value}")
                    for run in paragraph.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)
                            run.bold = True
                            run.underline = True
                            replaced = True
        
        if not replaced:
            app.logger.warning("Плейсхолдеры не обнаружены!")

        # Сохранение
        os.makedirs("temp", exist_ok=True)
        output_path = os.path.join("temp", filename)
        doc.save(output_path)
        app.logger.info(f"Документ сохранен: {output_path}")
        return output_path

    except Exception as e:
        app.logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        raise

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        errors = []
        form_data = request.form.to_dict()
        app.logger.info(f"Получены данные: {form_data}")

        # Валидация
        date_formatted = format_date(form_data.get("date"))
        expiry_formatted = format_date(form_data.get("expiry_date"))
        
        # ... (остальная логика валидации как в предыдущем коде)
        
        try:
            docx_path = fill_template(data, filename)
            return send_file(docx_path, as_attachment=True, download_name=filename)
        except Exception as e:
            errors.append("Ошибка генерации документа!")
            return render_template('form.html', errors=errors, form_data=form_data)
    
    return render_template('form.html')

if __name__ == '__main__':
    if not os.path.exists("temp"):
        os.makedirs("temp", mode=0o777)
    app.run(host='0.0.0.0', port=5000, debug=False)