import streamlit as st
import random
from main import generate_raw_names  # 👈 your function

st.set_page_config(
    page_title="AI Baby Name Generator",
    page_icon="👶",
    layout="centered"
)

# 🎨 UI Styling
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #eef2f7, #d9e4f5);
}

/* Title */
.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #1B5E20;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #555;
    margin-bottom: 25px;
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #4CAF50, #2E7D32);
    color: white;
    font-size: 18px;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* Tag container */
.tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 20px;
}

/* Tag style */
.tag {
    padding: 10px 16px;
    margin: 6px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 16px;
    color: white;

    animation: fadeIn 0.4s ease-in;
    transition: 0.2s;
}

.tag:hover {
    transform: scale(1.1);
}

/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

</style>
""", unsafe_allow_html=True)


# 🎯 Header
st.markdown('<div class="title">👶 AI Baby Name Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate names based on letter & length</div>', unsafe_allow_html=True)


# 🧩 Inputs
col1, col2 = st.columns(2)

with col1:
    human_type = st.selectbox("👤 Gender", ["boy", "girl"])
    letter = st.text_input("🔤 Starting Letter", max_chars=1)

with col2:
    length = st.number_input("📏 Name Length", min_value=2, max_value=10, step=1)


# 🚀 Button
generate = st.button("✨ Generate Names")


# 🎨 Color palette
colors = [
    "#2E7D32", "#1565C0", "#6A1B9A",
    "#EF6C00", "#C62828", "#00838F"
]


# ⚙️ Logic
if generate:
    if not letter.isalpha():
        st.error("⚠️ Please enter a valid letter")
    else:
        with st.spinner("✨ Generating names..."):
            raw_output = generate_raw_names(
                human_type,
                letter.upper(),
                int(length)
            )

        # 🔹 Convert response → clean list
        names = []
        for line in raw_output.split("\n"):
            name = line.strip().lstrip("12345. ").strip()
            if name:
                names.append(name)

        st.success("🎉 Names Generated!")

        # 🎯 Display Tags
        tag_html = '<div class="tags">'
        for name in names:
            color = random.choice(colors)
            tag_html += f'<div class="tag" style="background:{color}">👶 {name}</div>'
        tag_html += '</div>'

        st.markdown(tag_html, unsafe_allow_html=True)