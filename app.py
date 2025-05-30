import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(page_title="GMEX - Transcrição", page_icon="📝")

st.title("📝 GMEX - Transcrição de Reuniões")
st.markdown("Transforme reuniões em texto com alta precisão!")

modelo_opcao = st.selectbox(
    "Escolha a qualidade da transcrição:",
    ["Alta Qualidade (small)", "Média (base)", "Rápida (tiny)"]
)

modelo_map = {
    "Alta Qualidade (small)": "small",
    "Média (base)": "base",
    "Rápida (tiny)": "tiny"
}
modelo_selecionado = modelo_map[modelo_opcao]

uploaded_file = st.file_uploader("🎧 Envie seu arquivo de áudio", type=["mp3", "wav", "m4a", "aac", "ogg"])
if uploaded_file:
    with st.spinner(f"Carregando modelo Whisper ({modelo_selecionado})..."):
        model = whisper.load_model(modelo_selecionado)
    st.info(f"Arquivo recebido: {uploaded_file.name}, {uploaded_file.size//1024} KB")
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        audio_path = tmp.name

    with st.spinner("Transcrevendo... (pode demorar alguns minutos para alta qualidade)"):
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
