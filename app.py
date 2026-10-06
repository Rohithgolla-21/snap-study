import streamlit as st
from google import genai
from google.genai import types
import smtplib
from email.mime.text import MIMEText

from prompts import (
    SYSTEM_PROMPT,
    SUMMARY_REQUEST_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(page_title="Snap & Study", page_icon="📚", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def send_email(to_address, subject, body):
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)


def add_message(role, kind, content):
    st.session_state.messages.append(
        {"role": role, "kind": kind, "content": content}
    )
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong while studying this: {error}"


# Onboarding
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.subheader("Turn confusing pages into clear explanations.")
    st.caption(
        "Snap a question, diagram, textbook page, or handwritten note. "
        "Gemini explains it step by step."
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="Rohith")
        email = st.text_input(
            "Email for saved study summaries",
            placeholder="you@example.com",
        )
        submitted = st.form_submit_button("Start studying 🚀", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip() or "@" not in email:
            st.warning("Please enter your name and a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# Header + save action
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 Snap & Study")
    st.caption(f"Study session for {st.session_state.name}")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1
    if st.button(
        "📧 Save summary",
        disabled=send_disabled,
        use_container_width=True,
        help="Email a compact summary of this study session.",
    ):
        with st.spinner("Preparing your study notes..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        try:
            send_email(
                st.session_state.email,
                "Your Snap & Study notes",
                summary,
            )
            st.success("Saved to your email 📩")
        except Exception as error:
            st.error(f"Couldn't send the email: {error}")


if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)


user_input = st.chat_input(
    "Ask a question, or attach a photo of your study material",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Explain the study material in this image. "
            "Identify the main question or concept first."
        )

    with st.spinner("Thinking like your study buddy..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
