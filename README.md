# 📚 Snap & Study

Snap & Study is a Streamlit multimodal study assistant built with Gemini vision + chat.

A student can:
- Upload a photo of a question, diagram, textbook page, handwritten note, chart, or code.
- Ask follow-up questions in the same conversation.
- Get simple, step-by-step explanations.
- Email a compact revision summary with one click.

## Why this project?

The core MacroSnap pattern is reused:

**Onboard → Chat + Vision → Gemini summary → Action**

Instead of tracking food, Snap & Study turns messy study material into an interactive learning session.

## Tech stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- Gmail SMTP using Python's built-in `smtplib`

## Project structure

```text
snap_study/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add secrets

Copy:

```text
.streamlit/secrets.toml.example
```

to:

```text
.streamlit/secrets.toml
```

Fill in:

- `GEMINI_API_KEY`
- `GMAIL_ADDRESS`
- `GMAIL_APP_PASSWORD`

For Gmail, enable 2-Step Verification and create an App Password. Never put your normal Gmail password in the app.

### 4. Run

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub.
2. Create a new Streamlit Community Cloud app.
3. Select `app.py`.
4. In the app's Secrets settings, paste the values from your local `secrets.toml`.
5. Deploy.

**Never commit `.streamlit/secrets.toml`.**

## Core user flow

1. Student enters name + destination email.
2. Student uploads study material or types a question.
3. Gemini analyzes the image/text and explains it.
4. Student can continue asking follow-up questions.
5. `📧 Save summary` asks Gemini to summarize the full session.
6. Gmail SMTP sends the summary to the student's email.

## Future extensions

- Exam mode with hints before answers.
- "Teach me like I'm 10" mode.
- Difficulty slider.
- Flashcard generation.
- Quiz me from this page.
- Telugu + English explanations.
