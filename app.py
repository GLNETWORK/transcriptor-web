import os
import whisper
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from datetime import timedelta

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TRANSCRIPT_FOLDER = 'transcripts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

model = whisper.load_model("tiny")

# Crear carpeta uploads si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')


def dividir_por_minutos(transcription):
    resultado = ""
    current_minute = -1
    for segment in transcription['segments']:
        minuto = int(segment['start'] // 60)
        if minuto != current_minute:
            current_minute = minuto
            resultado += f"\n\n🕒 Minuto {minuto}:\n"
        resultado += segment['text'].strip() + " "
    return resultado.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript = None
    transcript_file = None
    if request.method == 'POST':
        archivo = request.files['file']
        if archivo:
            nombre = secure_filename(archivo.filename)
            ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre)
            archivo.save(ruta_archivo)

            resultado = model.transcribe(ruta_archivo, verbose=False, word_timestamps=False)
            texto_minutos = dividir_por_minutos(resultado)

            nombre_txt = os.path.splitext(nombre)[0] + ".txt"
            ruta_txt = os.path.join(TRANSCRIPT_FOLDER, nombre_txt)
            with open(ruta_txt, "w", encoding="utf-8") as f:
                f.write(texto_minutos)

            transcript = texto_minutos
            transcript_file = nombre_txt
    return render_template('index.html', transcript=transcript, transcript_file=transcript_file)

@app.route('/transcripts/<filename>')
def download(filename):
    return send_from_directory(TRANSCRIPT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
