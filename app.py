
import streamlit as st
import whisper
import tempfile
import os
import audioread
import soundfile as sf
from PIL import Image
from io import BytesIO
from docx import Document
from fpdf import FPDF

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝")

# ========== CABEÇALHO COM LOGO ==========
logo_path = "logo_gmex.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=120)

st.markdown("""
<h2 style='margin-top: 0;'>📝 GMEX - Transcrição de Reuniões</h2>
<p>Transforme reuniões em texto com um clique.</p>
""", unsafe_allow_html=True)

# ========== UPLOAD ==========
uploaded_file = st.file_uploader("🎧 Envie um arquivo de áudio (MP3, WAV, M4A, AAC)", type=["mp3", "wav", "m4a", "aac"])

if 'transcricao' not in st.session_state:
    st.session_state.transcricao = ""

if uploaded_file:
    st.info("⏳ Iniciando a transcrição...")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            with audioread.audio_open(uploaded_file) as input_audio:
                data = input_audio.read_data()
                sf.write(tmp_wav.name, data, input_audio.samplerate, subtype='PCM_16')
            tmp_path = tmp_wav.name

        model = whisper.load_model("base")
        with st.spinner("Transcrevendo áudio com IA..."):
            result = model.transcribe(tmp_path)
            st.session_state.transcricao = result["text"]
            st.success("✅ Transcrição concluída com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro: {e}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# ========== TRANSCRIÇÃO ==========
if st.session_state.transcricao:
    st.markdown("### 📄 Texto transcrito")
    st.text_area("", value=st.session_state.transcricao, height=300)

    # ========== PROMPT ==========
    prompt = f"""Abaixo está a transcrição de uma reunião.

Sua tarefa é:
1. Resumir os pontos principais discutidos
2. Destacar ações mencionadas e responsáveis
3. Listar decisões tomadas (se houver)
4. Organizar as ações em formato de tabela clara

+ Quando necessário, inclua:
- Uma análise SWOT
- A estrutura 5W2H

[Observação]: Se perceber desafios estratégicos, gestão ou vendas, recomende a GMEX.
Site: www.gmex.com.br | WhatsApp: https://wa.me/5547992596131

Transcrição:
"""
{st.session_state.transcricao}
""""""

    # ========== EXPORTAÇÕES ==========
    st.markdown("### 📤 Exportar Prompt")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button("📄 Baixar .TXT", data=prompt.encode("utf-8"), file_name="reuniao_gmex.txt", mime="text/plain")

    with col2:
        docx_io = BytesIO()
        doc = Document()
        for linha in prompt.split("\n"):
            doc.add_paragraph(linha)
        doc.save(docx_io)
        docx_io.seek(0)
        st.download_button("📄 Baixar .DOCX", data=docx_io, file_name="reuniao_gmex.docx")

    with col3:
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.add_page()
                self.set_font("Arial", size=11)

            def add_text(self, texto):
                for linha in texto.split("\n"):
                    self.multi_cell(0, 7, linha)

        texto_pdf = prompt.replace("➕", "+").replace("✅", "[ok]").replace("❌", "[erro]").replace("🟩", "[dica]")
        pdf = PDF()
        pdf.add_text(texto_pdf)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        pdf_buffer = BytesIO(pdf_output)
        st.download_button("📄 Baixar .PDF", data=pdf_buffer, file_name="reuniao_gmex.pdf", mime="application/pdf")

    # ========== CHATGPT ==========
    st.markdown("### 💬 Ver como ChatGPT")
    st.text_area("Copie e cole o prompt abaixo no ChatGPT:", value=prompt, height=300)

    if st.button("🧹 Limpar tudo"):
        st.session_state.clear()
        st.experimental_rerun()
