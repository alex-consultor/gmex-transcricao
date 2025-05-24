
import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝")

st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("Envie um arquivo de áudio e receba a transcrição automática.")

uploaded_file = st.file_uploader("Escolha um arquivo de áudio (MP3, WAV, M4A, AAC)", type=["mp3", "wav", "m4a", "aac"])

if 'transcricao' not in st.session_state:
    st.session_state.transcricao = ""

if uploaded_file:
    st.info("Iniciando a transcrição...")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        model = whisper.load_model("base")
        with st.spinner("Transcrevendo com IA..."):
            result = model.transcribe(tmp_path)
            st.session_state.transcricao = result["text"]
            st.success("✅ Transcrição concluída!")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if st.session_state.transcricao:
    st.markdown("### Transcrição:")
    st.text_area("", st.session_state.transcricao, height=300)

    st.download_button("📄 Baixar TXT", st.session_state.transcricao, file_name="transcricao.txt")
    if st.button("🧹 Limpar"):
        st.session_state.transcricao = ""
        st.experimental_rerun()
