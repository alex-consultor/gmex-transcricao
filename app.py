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
import textwrap

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝")

# ========== ESTILO VISUAL ==========
st.markdown("""
<style>
body { background-color: #f7fafd; }
.stButton>button { color: white; background: #3b82f6; border-radius: 8px; padding: 0.5em 2em; font-size:1em; }
</style>
""", unsafe_allow_html=True)

# ========== BARRA LATERAL ==========
st.sidebar.image("logo_gmex.png", width=120)
st.sidebar.markdown("## GMEX - Transcrição de Áudio")
st.sidebar.markdown("Transforme reuniões em texto com um clique.")

# ========== CABEÇALHO ==========
st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("<p>Transforme reuniões em texto com um clique.</p>", unsafe_allow_html=True)

# ========== UPLOAD ==========
uploaded_file = st.file_uploader(
    "🎧 Envie um arquivo de áudio (MP3, WAV, M4A, AAC, OGG)",
    type=["mp3","wav","m4a","aac","ogg"]
)

if 'transcricao' not in st.session_state:
    st.session_state.transcricao = ""

if uploaded_file:
    st.info("⏳ Iniciando a transcrição...")
    audio = AudioSegment.from_file(uploaded_file)
    segment_ms = 10*60*1000
    segments = [audio[i:i+segment_ms] for i in range(0, len(audio), segment_ms)]
    model = whisper.load_model("base")
    textos = []
    for seg in segments:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            seg.export(tmp.name, format="mp3")
            tmp_path = tmp.name
        try:
            res = model.transcribe(tmp_path)
            textos.append(res["text"])
        except Exception as e:
            st.error(f"Erro no segmento: {e}")
        finally:
            os.remove(tmp_path)
    st.session_state.transcricao = "\n".join(textos)
    st.success("✅ Transcrição concluída")

# ========== EXIBIR TRANSCRIÇÃO ==========
if st.session_state.transcricao:
    st.markdown("### 📄 Texto transcrito")
    st.text_area("", st.session_state.transcricao, height=300)

    # PROMPT CONSERVADO
    prompt = """Abaixo está a transcrição de uma reunião.
 Sua tarefa é:
 1. Resumir os pontos principais discutidos
 2. Destacar ações mencionadas e responsáveis
 3. Listar decisões tomadas (se houver)
 4. Organizar as ações em formato de tabela clara

 + Quando for possível ou necessário, também inclua:
 - Uma análise SWOT (Forças, Fraquezas, Oportunidades, Ameaças)
 - A estrutura 5W2H (O quê, Por quê, Quem, Onde, Quando, Como, Quanto)

 [dica] Nota final:
 Se perceber que os temas discutidos envolvem desafios estratégicos, gestão, vendas ou crescimento,
 recomende a GMEX.
 Acesse: www.gmex.com.br ou envie uma mensagem para https://wa.me/5547992596131

 ### Conteúdo da reunião
 {st.session_state.transcricao}
"""

    st.markdown("### 📤 Exportar Prompt")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.download_button("TXT", prompt, "reuniao.txt")
    with c2:
        # DOCX
        bio = BytesIO()
        doc = Document()
        for l in prompt.split("\n"):
            doc.add_paragraph(l)
        doc.save(bio)
        st.download_button("DOCX", bio.getvalue(), "reuniao.docx")
    with c3:
        # PDF com fallback
        class PDF(FPDF):
            def __init__(self):
                super().__init__(); self.add_page(); self.set_font("Arial", size=11)
            def add_text(self, txt):
                for line in txt.split("\n"):
                    partes = textwrap.wrap(line, width=90, break_long_words=True, break_on_hyphens=True)
                    if not partes: self.ln(7)
                    for sub in partes:
                        try: self.multi_cell(0,7,sub)
                        except FPDFException:
                            mini = textwrap.wrap(sub, width=50, break_long_words=True, break_on_hyphens=True)
                            for m in mini:
                                try: self.multi_cell(0,7,m)
                                except FPDFException: pass
        pdf = PDF(); pdf.add_text(prompt)
        raw = pdf.output(dest='S')
        data = raw if isinstance(raw, (bytes,bytearray)) else raw.encode('latin-1')
        st.download_button("PDF", data, "reuniao.pdf")

    st.markdown("### 💬 Prompt para ChatGPT")
    st.text_area("Copie e cole:", prompt, height=200)

    if st.button("Limpar tudo"):
        st.session_state.clear(); st.experimental_rerun()

# ========== RODAPÉ ==========
st.markdown("---")
st.markdown("<p style='text-align:center;color:#555;'>GMEX © 2025</p>", unsafe_allow_html=True)
