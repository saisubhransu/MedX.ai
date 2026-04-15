import streamlit as st
from openai import OpenAI
import json
import re
import os

# ---------------------------
# CONFIG (OPENROUTER)
# ---------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")  # 🔴 PUT YOUR KEY HERE
)

st.set_page_config(page_title="MedAssist AI", page_icon="🏥", layout="wide")
st.title("🏥 MedAssist AI - Hospital Expert System")

# ---------------------------
# EMERGENCY KEYWORDS
# ---------------------------
EMERGENCY_SIGNS = [
    "chest pain",
    "difficulty breathing",
    "unconscious",
    "severe bleeding",
    "heart attack",
    "stroke"
]

# ---------------------------
# CLEAN JSON FUNCTION
# ---------------------------
def clean_json(text):
    try:
        text = re.sub(r"```json|```", "", text)
        return json.loads(text.strip())
    except:
        return None

# ---------------------------
# EMERGENCY CHECK
# ---------------------------
def check_emergency(text):
    return any(word in text.lower() for word in EMERGENCY_SIGNS)

# ---------------------------
# OPENROUTER FUNCTION
# ---------------------------
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ---------------------------
# TABS
# ---------------------------
tab1, tab2, tab3 = st.tabs([
    "🧠 Symptom Checker",
    "🏥 Help Desk",
    "💬 General Chat"
])

# ===========================
# TAB 1: SYMPTOM CHECKER
# ===========================
with tab1:
    st.subheader("🧠 Describe your symptoms")

    user_input = st.text_area("Enter symptoms here")

    if st.button("Analyze Symptoms"):

        if not user_input.strip():
            st.warning("Please enter symptoms")

        elif check_emergency(user_input):
            st.error("🚨 EMERGENCY DETECTED! Seek immediate medical attention!")

        else:
            prompt = f"""
            You are a medical expert system.

            Respond ONLY in valid JSON.

            {{
              "possible_conditions": ["condition1", "condition2"],
              "urgency": "Low/Medium/High",
              "recommended_action": "text",
              "precautions": ["point1", "point2"]
            }}

            Symptoms: {user_input}
            """

            with st.spinner("Analyzing symptoms..."):
                response_text = ask_ai(prompt)

            data = clean_json(response_text)

            if not data:
                st.error("⚠️ Could not parse response. Showing raw output:")
                st.write(response_text)
            else:
                st.success("Analysis Complete")

                st.write("### 🧾 Possible Conditions")
                for cond in data["possible_conditions"]:
                    st.write(f"- {cond}")

                urgency = data["urgency"]

                if urgency == "High":
                    st.error(f"⚠️ Urgency: {urgency}")
                elif urgency == "Medium":
                    st.warning(f"⚠️ Urgency: {urgency}")
                else:
                    st.success(f"✅ Urgency: {urgency}")

                st.write("### 🏥 Recommended Action")
                st.write(data["recommended_action"])

                st.write("### 🛡 Precautions")
                for p in data["precautions"]:
                    st.write(f"- {p}")

# ===========================
# TAB 2: HELP DESK
# ===========================
with tab2:
    st.subheader("🏥 Hospital Help Desk")

    help_query = st.text_input("Ask about hospital services")

    if st.button("Get Help"):

        if not help_query.strip():
            st.warning("Please enter your query")

        else:
            prompt = f"""
            You are a hospital help desk assistant.

            Answer clearly:
            - Department guidance
            - Appointments
            - Visiting hours
            - Emergency info

            Query: {help_query}
            """

            with st.spinner("Fetching help..."):
                response_text = ask_ai(prompt)

            st.write(response_text)

# ===========================
# TAB 3: CHATBOT
# ===========================
with tab3:
    st.subheader("💬 Chat with MedAssist")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        st.chat_message(msg["role"]).markdown(msg["content"])

    user_msg = st.chat_input("Ask anything...")

    if user_msg:
        st.session_state.chat.append({"role": "user", "content": user_msg})
        st.chat_message("user").markdown(user_msg)

        prompt = f"""
        You are a medical assistant chatbot.
        Keep answers safe, short, and helpful.

        User: {user_msg}
        """

        with st.spinner("Thinking..."):
            reply = ask_ai(prompt)

        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)
import os

port = int(os.environ.get("PORT", 8501))

# Run Streamlit via command (handled in render)
