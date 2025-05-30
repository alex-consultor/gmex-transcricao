import streamlit as st
import whisper
from pydub import AudioSegment
from pydub.utils import which
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

# Configura ffmpeg para o pydub (não exibe na tela)
ffmpeg_path = which("ffmpeg")
AudioSegment.converter = ffmpeg_path

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
st.sidebar.markdown("### 👨‍💼 App desenvolvido por **Alex Medeiros**")

# ========== CABEÇALHO ==========
st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("<p>Transforme reuniões em texto com um clique.</p>", unsafe_allow_html=True)

# ========== UPLOAD ==========
if "transcricoes" not in st.session_state:
    st.session_state.transcricoes = []

# Para compatibilidade com o bloco de exportação abaixo:
if "transcricao" not in st.session_state:
    st.session_state.transcricao = ""

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
    # Use o modelo tiny para melhor compatibilidade com Streamlit Cloud
    model = whisper.load_model("tiny")
    st.session_state.transcricoes.clear()
    status = st.empty()
    progresso_geral = st.progress(0)
    total_arquivos = len(uploaded_files)
    tempo_inicio = time.time()
    total_blocos = 0
    blocos_processados = 0

    # Diagnóstico e contagem de blocos
    for audio_file in uploaded_files:
        if audio_file.size == 0:
            st.error(f"O arquivo {audio_file.name} está vazio.")
            continue
        ext = audio_file.name.split('.')[-1].lower()
        try:
            audio_temp = AudioSegment.from_file(audio_file, format=ext)
            total_blocos += len(audio_temp) // (10 * 60 * 1000) + 1
        except Exception as e:
            st.error(f"Erro ao abrir {audio_file.name}: {e}")
            st.exception(e)
            continue

    for idx, uploaded_file in enumerate(uploaded_files):
        if uploaded_file.size == 0:
            st.error(f"O arquivo {uploaded_file.name} está vazio.")
            continue

        ext = uploaded_file.name.split('.')[-1].lower()
        uploaded_file.seek(0)
        try:
            audio = AudioSegment.from_file(uploaded_file, format=ext)
        except Exception as e:
            st.error('❌ O áudio não pôde ser processado.')
            st.text(f'Erro técnico: {str(e)}')
            st.exception(e)
            st.stop()

        segment_ms = 10 * 60 * 1000
        segments = [audio[i:i+segment_ms] for i in range(0, len(audio), segment_ms)]
        transcricao_arquivo = []

        for j, seg in enumerate(segments):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                seg.export(tmp.name, format="mp3")
                tmp_path = tmp.name
            try:
                with st.spinner(f"Transcrevendo bloco {j+1} de {len(segments)} do arquivo {uploaded_file.name}..."):
                    res = model.transcribe(tmp_path)
                    texto = res["text"].strip()
        if texto:
            transcricao_arquivo.append(texto)
            st.info(f"Bloco {j+1}: {repr(texto[:80])}...")
            else:
            st.warning(f"Bloco {j+1} sem texto (vazio mesmo).")
            except Exception as e:
            st.error(f"Erro no bloco {j+1} do arquivo {uploaded_file.name}: {e}")
            st.exception(e)
            finally:
            os.remove(tmp_path)

            blocos_processados += 1
            tempo_passado = time.time() - tempo_inicio
            media_por_bloco = tempo_passado / blocos_processados if blocos_processados else 0
            tempo_restante = int(media_por_bloco * (total_blocos - blocos_processados))
            minutos = int(tempo_passado // 60)
            segundos = int(tempo_passado % 60)
            rest_min = int(tempo_restante // 60)
            rest_seg = int(tempo_restante % 60)

            status.write(
                f"⏱️ Tempo decorrido: {minutos:02d}:{segundos:02d} — Estimado restante: {rest_min:02d}:{rest_seg:02d} "
                f"– Arquivo {idx+1}/{total_arquivos}, Bloco {j+1}/{len(segments)}"
            )

        # Guarda a transcrição do arquivo processado
        st.session_state.transcricoes.append("\n".join(transcricao_arquivo))
        progresso_geral.progress((idx + 1) / total_arquivos)

    tempo_total = time.time() - tempo_inicio
    minutos = int(tempo_total // 60)
    segundos = int(tempo_total % 60)
    status.success(f"✅ Todos os arquivos foram transcritos com sucesso em {minutos:02d}:{segundos:02d}.")

    # Junta as transcrições de todos os arquivos para exibir e exportar (linha importante!)
    st.session_state.transcricao = "\n".join(st.session_state.transcricoes)

# ========== EXIBIÇÃO DA TRANSCRIÇÃO E EXPORTAÇÃO ==========
if st.session_state.transcricao:
    st.markdown("### 📄 Texto transcrito")
    st.text_area("", st.session_state.transcricao, height=300)

    # PROMPT CONSERVADO
    prompt = f"""Abaixo está a transcrição de uma reunião.
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
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.add_page()
                self.set_font("Arial", size=11)

            def add_text(self, texto):
                for linha in texto.split("\n"):
                    partes = textwrap.wrap(linha, width=90, break_long_words=True, break_on_hyphens=True)
                    if not partes:
                        self.ln(7)
                    for sub in partes:
                        try:
                            self.multi_cell(0, 7, sub)
                        except Exception:
                            mini_partes = textwrap.wrap(sub, width=50, break_long_words=True, break_on_hyphens=True)
                            for mp in mini_partes:
                                try:
                                    self.multi_cell(0, 7, mp)
                                except Exception:
                                    for ch in mp:
                                        try:
                                            self.multi_cell(0, 7, ch)
                                        except Exception:
                                            pass

        texto_pdf = (
            prompt
            .replace("➕", "+")
            .replace("✅", "[ok]")
            .replace("❌", "[erro]")
            .replace("🟩", "[dica]")
        )
        pdf = PDF()
        pdf.add_text(texto_pdf)
        raw = pdf.output(dest="S")
        pdf_bytes = raw if isinstance(raw, (bytes, bytearray)) else raw.encode("latin-1")
        pdf_buffer = BytesIO(pdf_bytes)
        st.download_button(
            "📄 Baixar .PDF",
            data=pdf_buffer,
            file_name="reuniao_gmex.pdf",
            mime="application/pdf"
        )

    st.markdown("### 💬 Ver como ChatGPT")
    st.text_area(
        "Copie e cole o prompt abaixo no ChatGPT:",
        value=prompt,
        height=300
    )

    # ✅ Executa a limpeza com segurança usando flag
if "limpar_flag" in st.session_state:
    st.session_state.clear()
    st.stop()  # Garante que o app pare aqui e reinicie limpo

# ✅ Botão de limpar (com key única)
if st.button("🧹 Limpar tudo", key="botao_limpar"):
    st.session_state["limpar_flag"] = True
    st.experimental_rerun()
