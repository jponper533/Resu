import os
import docx2txt
import PyPDF2
import torch
from transformers import LEDTokenizer, LEDForConditionalGeneration

# Cargar modelo y tokenizer
model_name = "allenai/led-base-16384"
tokenizer = LEDTokenizer.from_pretrained(model_name)
model = LEDForConditionalGeneration.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Leer archivos
def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.docx':
        return docx2txt.process(path)
    elif ext == '.pdf':
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        return text
    elif ext == '.txt':
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Resumen preciso de texto largo
def summarize_text(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=16000
    )

    input_ids = inputs["input_ids"].to(device)

    # Global attention en el primer token
    global_attention_mask = torch.zeros_like(input_ids)
    global_attention_mask[:, 0] = 1

    summary_ids = model.generate(
        input_ids,
        global_attention_mask=global_attention_mask,
        max_length=1000,
        min_length=350,
        num_beams=4,
        length_penalty=2.0,
        no_repeat_ngram_size=3
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# -------- MAIN --------
file_path = input("Ingrese la ruta del archivo: ").strip()

if not file_path:
    print("No se seleccionó archivo.")
else:
    text = read_file(file_path)
    if not text.strip():
        print("Archivo vacío.")
    else:
        summary = summarize_text(text)

        output_file = os.path.join(
            os.path.dirname(file_path),
            "resumen_" + os.path.basename(file_path) + ".txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Resumen generado correctamente:")
        print(output_file)
