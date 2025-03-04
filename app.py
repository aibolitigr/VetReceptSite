from flask import Flask, render_template, request, send_file
from docx import Document
import os
import requests  # Используем CloudConvert API для конвертации

app = Flask(__name__)
CLOUDCONVERT_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNmY1ZTJlNmRhMWRjZjg1NDQ1MTNjNzU2NTJmMTQ5OGJjN2QwYmExN2E3NDY2NWI5YTNlYTYzZGFjNjNmM2RmNmQzMzNjMWM4MDVlMzk3MTEiLCJpYXQiOjE3NDExMTU1OTQuMTc1MDQxLCJuYmYiOjE3NDExMTU1OTQuMTc1MDQyLCJleHAiOjQ4OTY3ODkxOTQuMTcwNjY5LCJzdWIiOiI3MTIzNDM4NCIsInNjb3BlcyI6W119.iEL3aAuipfE2tl51-WBh1rpK1Wl5G5r17vzrtUdZNl0o_kcVruyg-tMx35jCUk_m4qWqAvgIhBtCHtMYK-sRVBZKLqDSRBFn1mVUhIbVspY60ByBa1Baxdx5uQaBDDjVp8oV2fuUnqoP6xOFwUbg9zUNtulIcpVhWM2tFb_p2oOsTpYTjwvaD2721CB8l9wb0GXTfDv0rapm07BzVIt9n62WXhkh46t-pjNCyvLtLVCuD114hlup_nfxrQrJ5nxADJOAyVEyIEjV_gSGXZBcv75Iv-wuP-OXBtbloog6NjAOxuUJgREqd12LtH9SJYiCTmVKFhXfUS18Kg4cGiL8b7OpsJ5lKRifV6m7Boze-MncZzPSTtOJ_M5ijWIVYazhm7igF8G7MgNUtVdov1j_u3GY3ckRmUL_mJmPWXi2vWZI2uNjJO-8XVtATLuxRrI0lg8eJbUTrgjJAKteAeKonWxwreIDPSST03-lL4w-fgkD8CFcFjAPSpBD_hS_jmor-PEeNAvp-1UQm5-VOj29NTkub-f3B-5ob0RfurO79x5J2BPYbKzaHk3xCOq7WEKBFIABA98J2LHtIcvJlWOc-RlN5jKoc4p9XpX5o62Lrf6Sx6uiCr9-jxjWkhIRzXR_kWV_A2h_k7R-eIlIAzODThkmKhbhbrp_Sm4hvwLNvJ0"  # 🔹 Замени на свой API-ключ


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
    print("[INFO] Конвертация DOCX в PDF через CloudConvert API...")
    
    files = {"file": open(docx_path, "rb")}
    headers = {"Authorization": f"Bearer {CLOUDCONVERT_API_KEY}"}
    
    try:
        response = requests.post("https://api.cloudconvert.com/v2/convert", headers=headers, files=files, data={
            "inputformat": "docx",
            "outputformat": "pdf"
        })
        response.raise_for_status()
        
        pdf_url = response.json()["data"]["output"]["url"]
        pdf_response = requests.get(pdf_url)
        
        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)
        
        print("[INFO] PDF-файл успешно загружен:", pdf_path)
        return pdf_path
    except Exception as e:
        print("[ERROR] Ошибка при конвертации в PDF:", e)
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
