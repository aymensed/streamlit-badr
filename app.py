import streamlit as st
import joblib
import os

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(
    page_title="SQL Injection Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL_PATH = "CODE/svm_sqli_model.joblib"
VECTORIZER_PATH = "CODE/vectorizer.joblib"

# ==============================
# SESSION STATE (AVANT WIDGETS)
# ==============================
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# ==============================
# LOAD MODELS (CACHED)
# ==============================
@st.cache_resource
def load_models():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        st.error("❌ Model files not found.")
        st.stop()

    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
    return vectorizer, model

vectorizer, model = load_models()

# ==============================
# PREDICTION FUNCTION
# ==============================
def predict_sqli(text: str):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return bool(pred)

# ==============================
# CALLBACK (SAFE)
# ==============================
def load_example(text):
    st.session_state.query_input = text

# ==============================
# UI
# ==============================
st.markdown("<h1 style='text-align:center;'>🛡️ SQL Injection Detection</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>SVM + TF-IDF | Streamlit Cloud</p>", unsafe_allow_html=True)

st.markdown("---")

# INPUT + BUTTON
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_area(
        "SQL Query",
        key="query_input",
        height=150,
        placeholder="Ex: ' OR 1=1 --"
    )

with col2:
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)
    analyze = st.button("Analyze", type="primary", use_container_width=True)

# ==============================
# EXAMPLES (SAFE BUTTONS)
# ==============================
with st.expander("📌 Try examples"):
    ex_cols = st.columns(4)

    ex_cols[0].button(
        "Normal SELECT",
        on_click=load_example,
        args=("SELECT name FROM users;",)
    )

    ex_cols[1].button(
        "SQLi OR 1=1",
        on_click=load_example,
        args=("' OR 1=1 --",)
    )

    ex_cols[2].button(
        "Normal UPDATE",
        on_click=load_example,
        args=("UPDATE products SET price=10 WHERE id=5;",)
    )

    ex_cols[3].button(
        "SQLi DROP",
        on_click=load_example,
        args=("'; DROP TABLE users--",)
    )

# ==============================
# RESULT
# ==============================
if analyze:
    if user_input.strip() == "":
        st.warning("⚠️ Please enter a SQL query.")
    else:
        with st.spinner("Analyzing..."):
            is_sqli = predict_sqli(user_input)

        st.markdown("---")
        st.subheader("Result")

        if is_sqli:
            st.error("🚨 SQL INJECTION DETECTED")
        else:
            st.success("✅ NORMAL QUERY")

        st.code(user_input, language="sql")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>© 2026 | SQL Injection Detection App</p>",
    unsafe_allow_html=True
)
