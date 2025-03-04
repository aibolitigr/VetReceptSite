from flask import Flask, render_template, request, send_file
from docx import Document
import os
from weasyprint import HTML, CSS  # Используем WeasyPrint для конвертации в PDF

app = Flask(__name__)

def fill_template(data):
    template_path = "template.docx"  # Файл шаблона
    output_path = "filled_recipe.docx"
    
    print("[INFO] Открываем шаблон Word...")
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, value)
    
    doc.save(output_path)
    print("[INFO] Word-файл сохранён:", output_path)
    return output_path

def convert_to_pdf(docx_path):
    pdf_path = docx_path.replace(".docx", ".pdf")
    html_path = docx_path.replace(".docx", ".html")
    
    print("[INFO] Конвертация DOCX в HTML...")
    doc = Document(docx_path)
    html_content = "".join([f"<p>{p.text}</p>" for p in doc.paragraphs])
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                body {{ font-family: 'DejaVu Sans', sans-serif; }}
            </style>
        </head>
        <body>{html_content}</body>
        </html>
        """)
    
    print("[INFO] Конвертация HTML в PDF с помощью WeasyPrint...")
    HTML(html_path).write_pdf(pdf_path, stylesheets=[CSS(string="body { font-family: 'DejaVu Sans', sans-serif; }")])
    
    if os.path.exists(pdf_path):
        print("[INFO] PDF-файл успешно создан:", pdf_path)
        return pdf_path
    else:
        print("[ERROR] PDF-файл не найден после конвертации!")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            "{instance_number}": request.form.get("instance_number"),
            "{recipe_number}": request.form.get("recipe_number"),
            "{date}": request.form.get("date"),
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
            "{expiry_date}": request.form.get("expiry_date")
        }
        
        docx_path = fill_template(data)
        pdf_path = convert_to_pdf(docx_path)
        
        if pdf_path:
            return send_file(pdf_path, as_attachment=True)
        else:
            return "Ошибка при создании PDF-файла. Проверьте логи в консоли."
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Заполнение рецепта</title>
    </head>
    <body>
        <h2>Введите данные для рецепта</h2>
        <form method="POST">
            <label>Номер экземпляра:</label>
            <input type="text" name="instance_number" required><br>
            <label>Номер рецепта:</label>
            <input type="text" name="recipe_number" required><br>
            <label>Дата:</label>
            <input type="date" name="date" required><br>
            <label>ФИО владельца и адрес:</label>
            <input type="text" name="owner_name" required><br>
            <label>Информация о животном:</label>
            <input type="text" name="pet_info" required><br>
            <label>Название препарата:</label>
            <input type="text" name="medicine" required><br>
            <label>Общая доза:</label>
            <input type="text" name="dosage" required><br>
            <label>Разовая доза:</label>
            <input type="text" name="single_dose" required><br>
            <label>Частота приёма:</label>
            <input type="text" name="frequency" required><br>
            <label>Время приёма:</label>
            <input type="text" name="time_of_day" required><br>
            <label>Длительность приёма:</label>
            <input type="text" name="duration" required><br>
            <label>Способ введения:</label>
            <input type="text" name="method" required><br>
            <label>Время приёма относительно еды:</label>
            <input type="text" name="feeding_time" required><br>
            <label>ФИО ветеринарного врача:</label>
            <input type="text" name="vet_name" required><br>
            <label>Срок действия рецепта:</label>
            <input type="date" name="expiry_date" required><br>
            <button type="submit">Сгенерировать PDF</button>
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
