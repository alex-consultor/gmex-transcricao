import streamlit as st
import whisper
from pydub import AudioSegment
from PIL import Image
import tempfile
import os
from io import BytesIO
from docx import Document
from fpdf import FPDF
from fpdf.errors import FPDFException
import time
import textwrap

# ========== FUNÇÕES AUXILIARES ==========
def DocumentToBytes(text):
    bio = BytesIO()
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(bio)
    return bio.getvalue()


def PDFToBytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    raw = pdf.output(dest="S")
    return raw if isinstance(raw, (bytes, bytearray)) else raw.encode("latin-1")

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝", layout="wide")

# ========= CSS CUSTOMIZADO ==========
st.markdown("""
<style>
body { background-color: #f7fafd; }
.header-section { text-align: center; margin-bottom: 2rem; }
.metric-card { background: #fff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ========= HERO SECTION ==========
st.markdown("<div class='header-section'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 6, 2])
with col2:
    st.image("logo_gmex.png", width=150)
    st.markdown("# 📝 GMEX Transcrição de Reuniões", unsafe_allow_html=True)
    st.markdown("<p>Transforme suas reuniões em textos precisos usando IA.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ========= BARRA LATERAL ==========
st.sidebar.image("logo_gmex.png", width=120)
st.sidebar.markdown("## GMEX - Transcrição de Áudio")
st.sidebar.markdown("Transforme reuniões em texto com um clique.")
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido por:** Alex Medeiros, Consultor GMEX")
st.sidebar.markdown("---")
st.sidebar.markdown("## Sobre a GMEX")
st.sidebar.markdown(
    "🚀 Acelere seus resultados com consultoria comercial.\n"
    "💡 Estratégias personalizadas e equipes de alta performance.\n"
    "🔗 [Conheça nossos serviços](https://www.gmex.com.br)"
)

# ========= UPLOAD ==========
st.markdown("## 🎧 Envie seu áudio")
uploaded_file = st.file_uploader(
    "Suporta: MP3, WAV, M4A, AAC, OGG", type=["mp3", "wav", "m4a", "aac", "ogg"]
)

if 'transcricao' not in st.session_state:
    st.session_state.transcricao = ""

if uploaded_file:
    st.info("⏳ Iniciando a transcrição...")
    audio = AudioSegment.from_file(uploaded_file)
    duration_ms = len(audio)
    segment_ms = 10 * 60 * 1000  # 10 minutos
    segments = [audio[i:i + segment_ms] for i in range(0, duration_ms, segment_ms)]
    total = len(segments)

    # exibindo métricas iniciais
    m1, m2, m3 = st.columns(3)
    m1.metric("Duração (min)", round(duration_ms/60000, 1))
    m2.metric("Blocos", total)
    m3.metric("Modelo", "Whisper base")

    progress_bar = st.progress(0)
    eta_text = st.empty()
    start_time = time.time()
    model = whisper.load_model("base")
    textos = []

    for idx, seg in enumerate(segments):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            seg.export(tmp.name, format="mp3")
            tmp_path = tmp.name
        try:
            result = model.transcribe(tmp_path)
            textos.append(result["text"])
        except Exception as e:
            st.error(f"❌ Erro no bloco {idx+1}: {e}")
        finally:
            os.remove(tmp_path)
        elapsed = time.time() - start_time
        avg = elapsed / (idx + 1)
        remaining = avg * (total - idx - 1)
        eta_text.text(f"Bloco {idx+1}/{total} — ETA: {int(remaining)}s")
        progress_bar.progress((idx + 1) / total)

    st.session_state.transcricao = "\n".join(textos)
    st.success("✅ Transcrição concluída")

# ========= RESULTADOS ==========
if st.session_state.transcricao:
    st.subheader("📄 Transcrição Completa")
    st.text_area("", st.session_state.transcricao, height=300)

    prompt = f"""Abaixo está a transcrição...
{st.session_state.transcricao}
"""
    st.subheader("💬 Prompt para ChatGPT")
    st.text_area("Copie e cole no ChatGPT:", prompt, height=200)

    st.subheader("📤 Exportar Prompt")
    b1, b2, b3 = st.columns(3)
    b1.download_button("TXT", prompt, "transcricao.txt")
    b2.download_button(
        "DOCX",
        data=BytesIO(DocumentToBytes(prompt)),
        file_name="transcricao.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    b3.download_button(
        "PDF",
        data=BytesIO(PDFToBytes(prompt)),
        file_name="transcricao.pdf",
        mime="application/pdf"
    )

# ========= RODAPÉ ==========
st.markdown("---")
st.markdown("<p style='text-align:center; color:#555;'>© 2025 GMEX - Todos os direitos reservados</p>", unsafe_allow_html=True)
