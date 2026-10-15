import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io

def limpiar_pdf_f210(pdf_path, output_path):
    # Abrir el documento PDF
    doc = fitz.open(pdf_path)
    nuevo_doc = fitz.open()

    for i, pagina in enumerate(doc):
        # Renderizar la página a imagen de alta resolución (300 DPI)
        pix = pagina.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        
        # Abrir con Pillow
        img = Image.open(io.BytesIO(img_data)).convert("L")
        
        # Aplicar un umbral (threshold) para eliminar el fondo gris/punteado 
        # y volver completamente blanco el fondo y negro puro los trazos.
        # Ajusta el valor de corte (ej. 180-200) según qué tan marcadas estén las líneas.
        umbral = 190
        img_limpia = img.point(lambda p: 255 if p > umbral else 0, '1')
        
        # Opcional: Volver a convertir a escala de grises/RGB para guardar en PDF
        img_final = img_limpia.convert("RGB")
        
        # Guardar la página procesada en un nuevo PDF
        img_pdf_bytes = io.BytesIO()
        img_final.save(img_pdf_bytes, format="PDF")
        img_pdf_bytes.seek(0)
        
        temp_doc = fitz.open("pdf", img_pdf_bytes.read())
        nuevo_doc.insert_pdf(temp_doc)

    # Guardar el resultado final limpio y definido
    nuevo_doc.save(output_path)
    nuevo_doc.close()
    doc.close()
    print(f"¡PDF optimizado guardado exitosamente en: {output_path}!")

# Ejemplo de ejecución:
# limpiar_pdf_f210("registro_Único_de_contribuyentes_(f-210) (1).pdf", "F-210_nítido.pdf")