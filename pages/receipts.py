import streamlit as st
from utils.file_utils import save_uploaded_file

def show():
    st.markdown("## 📸 Upload Receipts")
    st.write("Upload receipt images or PDFs and store them in your receipts folder.")

    uploaded_file = st.file_uploader("Choose a receipt file", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file)
        st.success(f"Receipt saved to: `{file_path}`")
        if uploaded_file.type.startswith("image/"):
            st.image(uploaded_file, caption="Preview", use_column_width=True)
        elif uploaded_file.type == "application/pdf":
            st.markdown("📄 PDF uploaded. (Preview not available)")
