import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("Limpiador de Trazos para Formularios PDF")
st.write("Sube tu formulario PDF escaneado para eliminar el fondo gris/punteado y dejar los trazos nítidos.")

# Componente para subir el archivo PDF
uploaded_file = st.file_uploader("Elige un archivo PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Leer los bytes del PDF subido
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        nuevo_doc = fitz.open()

        with st.spinner("Procesando y limpiando el documento..."):
            for pagina in doc:
                # Renderizar la página a imagen de alta resolución (300 DPI)
                pix = pagina.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                
                # Abrir con Pillow y convertir a escala de grises
                img = Image.open(io.BytesIO(img_data)).convert("L")
                
                # Aplicar un umbral (threshold) para eliminar el fondo gris y oscurecer los trazos
                umbral = 190
                img_limpia = img.point(lambda p: 255 if p > umbral else 0)
                
                # Convertir de vuelta a RGB (evita problemas de visualización en negro)
                img_final = img_limpia.convert("RGB")
                
                # Guardar la página procesada en un PDF temporal
                img_pdf_bytes = io.BytesIO()
                img_final.save(img_pdf_bytes, format="PDF")
                img_pdf_bytes.seek(0)
                
                temp_doc = fitz.open(stream=img_pdf_bytes.read(), filetype="pdf")
                nuevo_doc.insert_pdf(temp_doc)

            # Guardar el resultado final en memoria
            output_pdf_bytes = nuevo_doc.write()
            nuevo_doc.close()
            doc.close()

        st.success("¡Documento procesado con éxito!")

        # Botón de descarga para el usuario
        st.download_button(
            label="Descargar PDF Nítido",
            data=output_pdf_bytes,
            file_name="formulario_nitido.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
