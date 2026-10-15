import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageFilter
import io

st.set_page_config(page_title="Optimizador de Trazos DTE y Formularios", layout="centered")

st.title("Optimizador Avanzado de Formularios")
st.write("Sube tu PDF para eliminar el tramado punteado y redefinir las líneas y textos con total nitidez.")

# Panel de control lateral para afinar el resultado
st.sidebar.header("Ajustes de Nitidez")
umbral = st.sidebar.slider("Umbral de Blancos/Negros", min_value=120, max_value=230, value=185, help="Un valor más alto oscurece y une mejor los trazos punteados.")
fortalecer = st.sidebar.checkbox("Fortalecer y engrosar líneas (Recomendado)", value=True, help="Elimina los puntos dispersos y hace las líneas continuas.")

uploaded_file = st.file_uploader("Selecciona el archivo PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        nuevo_doc = fitz.open()

        with st.spinner("Procesando y redefiniendo trazos..."):
            for pagina in doc:
                # Renderizar a alta resolución (300 DPI para máxima definición)
                pix = pagina.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                
                # Convertir a escala de grises
                img = Image.open(io.BytesIO(img_data)).convert("L")
                
                # Aplicar umbral para limpiar el fondo grisáceo por completo
                img_limpia = img.point(lambda p: 255 if p > umbral else 0)
                
                # Si se activa, aplicamos un filtro de dilatación/mínimo para engrosar trazos punteados
                if fortalecer:
                    # El filtro min (MinFilter) expande las zonas oscuras (negro), uniendo los puntos
                    img_limpia = img_limpia.filter(ImageFilter.MinFilter(3))
                
                # Convertir a RGB para asegurar compatibilidad de visualización
                img_final = img_limpia.convert("RGB")
                
                # Guardar página procesada
                img_pdf_bytes = io.BytesIO()
                img_final.save(img_pdf_bytes, format="PDF")
                img_pdf_bytes.seek(0)
                
                temp_doc = fitz.open(stream=img_pdf_bytes.read(), filetype="pdf")
                nuevo_doc.insert_pdf(temp_doc)

            output_pdf_bytes = nuevo_doc.write()
            nuevo_doc.close()
            doc.close()

        st.success("¡Proceso completado con éxito!")

        st.download_button(
            label="Descargar PDF con Trazos Definidos",
            data=output_pdf_bytes,
            file_name="formulario_trazos_perfectos.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
