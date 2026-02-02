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

def clean_summary(text):
    """Elimina frases incompletas al final del resumen"""
    # Marcadores de fin de oración
    sentence_endings = ['.', '!', '?']
    
    # Buscar el último signo de puntuación válido
    last_position = -1
    for ending in sentence_endings:
        pos = text.rfind(ending)
        if pos > last_position:
            last_position = pos
    
    # Si encontramos un signo de puntuación para
    if last_position != -1 and last_position > len(text) * 0.3:
        return text[:last_position + 1].strip()
    
    # Si no hay puntuación clara, retornar el texto original
    return text.strip()

def chunk_text(text, max_tokens=2000):
    """Divide el texto en chunks respetando límites de palabras"""
    tokens = tokenizer.encode(text)
    
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens)
        
        # Si no es el último chunk, buscar el último espacio para no cortar palabras
        if i + max_tokens < len(tokens):
            last_space = chunk_text.rfind(' ')
            if last_space > len(chunk_text) * 0.7:
                chunk_text = chunk_text[:last_space]
        
        if chunk_text.strip():
            yield chunk_text.strip()

def summarize_long_text(text):
    """Resume textos largos preservando contexto entre chunks"""
    partial_summaries = []
    chunks = list(chunk_text(text))
    
    # Si el texto cabe en un chunk, resumir directamente
    if len(chunks) == 1:
        return summarize_text(text)
    
    # Procesar cada chunk
    for chunk in chunks:
        partial_summaries.append(summarize_text(chunk))
    
    # Combinar resúmenes con contexto y hacer resumen final
    combined = " ".join(partial_summaries)
    return summarize_text(combined)


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
        max_length=12000
    )

    input_ids = inputs["input_ids"].to(device)


    # Global attention en el primer token
    global_attention_mask = torch.zeros_like(input_ids)
    global_attention_mask[:, 0] = 1

    summary_ids = model.generate(
        input_ids,
        global_attention_mask=global_attention_mask,
        max_length=500,
        min_length=100,
        num_beams=5,
        length_penalty=3.0,
        no_repeat_ngram_size=2,
        early_stopping=True,
        temperature=0.7,
        do_sample=False
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return clean_summary(summary)