# Resumidor de texto (.txt, .docx, .pdf)

Este script utiliza **allenai/led-base-16384** para generar resúmenes de mejor calidad y también es capaz de procesar archivos **PDF** utilizando **pytesseract** para extraer texto de los documentos **PDF**. Al momento de ejecutarlo solicita al usuario la ubicación del archivo. Permite al usuario seleccionar un archivo y luego resume ese archivo. El resúmen se escribira en el campo de texto de abajo

**summarizer.py** permite al usuario ingresar un archivo de los disponibles indicados (hasta un maximo de 100 palabras el archivo), tras darle al boton de generar resumen procedera a darle un texto resumido basado en el original 

## Repositorio base
https://github.com/Yextep/Resu


## Instalación

Accedemos a las carpetas
```bash
cd Resu/resumidor
```
Instalamos requerimientos
```bash
pip install -r requeriments.txt
```
Ejecutamos el Script
```bash
python3 summarizer.py
```
