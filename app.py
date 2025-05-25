
import streamlit as st
import whisper
from pydub import AudioSegment
from PIL import Image
import tempfile
import os
from io import BytesIO
from docx import Document
from fpdf import FPDF
import textwrap
import time

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
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Sobre a GMEX")
st.sidebar.markdown("""
**GMEX** é uma consultoria especializada em estratégias comerciais e desenvolvimento de times de alta performance.

- 📊 Clareza estratégica  
- 🎯 Aumento de resultados  
- 🧠 Cultura comercial forte  
- 🤝 Desenvolvimento de líderes

[🌐 www.gmex.com.br](https://www.gmex.com.br)  
[📲 Fale conosco no WhatsApp](https://wa.me/5547992596131)
""")
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 App desenvolvido por **Alex Medeiros**")

# ========== CABEÇALHO ==========
st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("<p>Transforme reuniões em texto com um clique.</p>", unsafe_allow_html=True)

# ========== UPLOAD ==========
if "transcricoes" not in st.session_state:
    st.session_state.transcricoes = []

uploaded_files = st.file_uploader(
    "🎧 Envie os arquivos de áudio (em sequência)",
    type=["mp3", "wav", "m4a", "aac", "ogg"],
    accept_multiple_files=True
)

st.warning("⚠️ Cada arquivo deve ter no máximo 200MB.")

with st.expander("💡 Áudio maior que 200MB? Use o InParts"):
    st.markdown("""
**InParts** é um programa gratuito da GMEX que divide áudios grandes em partes de até 10 minutos.

🔹 Compatível com `.m4a`, `.mp3`, `.wav`  
🔹 Simples, leve e fácil de usar  
🔹 Ideal para preparar arquivos grandes para este app

👉 [Clique aqui para baixar o InParts (Instalador .exe)](https://drive.google.com/uc?export=download&id=1dEfJVVqERYQYYCIEPXJ6zuue_Vwu9Gdu)

Após instalar:
1. Abra o programa
2. Selecione o áudio grande
3. Escolha onde salvar os blocos gerados
4. Suba os arquivos divididos aqui na GMEX - Transcrição

> Desenvolvido por [GMEX - Estratégia Comercial](https://www.gmex.com.br)
""")

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    model = whisper.load_model("base")
    st.session_state.transcricoes.clear()
    status = st.empty()
    progresso_geral = st.progress(0)
    total_arquivos = len(uploaded_files)
    tempo_inicio = time.time()

    for idx, uploaded_file in enumerate(uploaded_files):
        status.write(f"🔄 Processando arquivo {idx+1}/{total_arquivos}: {uploaded_file.name}")
        audio = AudioSegment.from_file(uploaded_file)
        segment_ms = 10 * 60 * 1000
        segments = [audio[i:i+segment_ms] for i in range(0, len(audio), segment_ms)]
        transcricao_arquivo = []

        for j, seg in enumerate(segments):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                seg.export(tmp.name, format="mp3")
                tmp_path = tmp.name
            try:
                status.write(f"🎙️ {uploaded_file.name} – Bloco {j+1}/{len(segments)}")
                res = model.transcribe(tmp_path)
                texto = res["text"].strip()
                if texto and len(texto) > 15 and "inaudível" not in texto.lower():
                    transcricao_arquivo.append(texto)
            except Exception as e:
                st.error(f"Erro no bloco {j+1} do arquivo {uploaded_file.name}: {e}")
            finally:
                os.remove(tmp_path)

        st.session_state.transcricoes.append("\n".join(transcricao_arquivo))
        progresso_geral.progress((idx + 1) / total_arquivos)

    tempo_total = time.time() - tempo_inicio
    minutos = int(tempo_total // 60)
    segundos = int(tempo_total % 60)
    status.success(f"✅ Todos os arquivos foram transcritos com sucesso em {minutos:02d}:{segundos:02d}.")
