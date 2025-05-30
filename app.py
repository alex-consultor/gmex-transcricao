import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝")

st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("Transforme reuniões em texto com rapidez!")

uploaded_file = st.file_uploader("🎧 Envie seu arquivo de áudio", type=["mp3", "wav", "m4a", "aac", "ogg"])
if uploaded_file:
    with st.spinner("Carregando modelo Whisper..."):
        model = whisper.load_model("tiny")  # O mais rápido
    st.info(f"Arquivo recebido: {uploaded_file.name}, {uploaded_file.size//1024} KB")
    # Salva o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        audio_path = tmp.name

    with st.spinner("Transcrevendo..."):
        try:
            result = model.transcribe(audio_path, language="pt")
            texto = result["text"].strip()
            if texto:
                st.success("Transcrição concluída!")
                st.text_area("Texto transcrito", texto, height=300)
                st.download_button("Baixar TXT", texto, file_name="transcricao.txt")
            else:
                st.warning("O áudio foi processado, mas não foi detectada fala clara.")
        except Exception as e:
            st.error(f"Erro na transcrição: {e}")

    os.remove(audio_path)
