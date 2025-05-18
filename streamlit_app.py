import streamlit as st
import openai
import time
import fitz  # PyMuPDF


# Set your OpenAI API key
openai.api_key = st.secrets.get("OPENAI_API_KEY")

st.set_page_config(page_title="Claim Analyzer", layout="wide")
st.title("💼 Insurance Claim Settlement Analyzer")

# Sidebar: Uploads, Model Selection, Custom Prompt
with st.sidebar:
    st.header("📁 Upload Files & Settings")

    policy_pdf = st.file_uploader("📄 Policy Wording PDF", type="pdf")
    bill_pdf = st.file_uploader("🏥 Discharge Summary / Bill PDF", type="pdf")

    model_choice = st.selectbox("🧠 OpenAI Model", ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"], index=1)

    custom_prompt = st.text_area("✍️ Custom Prompt (optional)", placeholder="Leave blank to use default system prompt", height=200)

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# Default system prompt
default_system_prompt = """
You are a diligent insurance claim settlement expert.

You will be given:
1. The insurance **Policy Wording** text – which outlines what is covered and not covered.
2. A **Discharge Summary or Hospital Bill** – which lists the medical procedures, diagnoses, and charges.

Your job is to:
- Carefully match the charges from the hospital document with what's covered in the policy.
- Calculate what portion of the total bill is **approved for settlement** based on the policy.
- Clearly summarize the **approved items**, **rejected items** (and why), and the **final approved amount**.

Be strict but fair and include all rationale used for decision-making.
"""

# Main logic
if policy_pdf and bill_pdf:
    if st.button("🚀 Analyze Claim"):
        with st.spinner("Reading PDFs and analyzing..."):

            # Extract text from PDFs
            policy_text = extract_text_from_pdf(policy_pdf)
            bill_text = extract_text_from_pdf(bill_pdf)

            # Compose final message to model
            prompt = custom_prompt.strip() if custom_prompt.strip() else default_system_prompt

            user_message = f"""
Below are two documents.

---

**Insurance Policy Wording:**

{policy_text}

---

**Discharge Summary / Hospital Bill:**

{bill_text}

---

Based on these documents, perform the insurance claim analysis as per the instructions.
"""

            # Call OpenAI chat completion
            response = openai.ChatCompletion.create(
                model=model_choice,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            # Display result
            st.success("✅ Analysis Complete")
            st.markdown("### 🧾 Claim Decision Summary")
            st.markdown(response["choices"][0]["message"]["content"])
else:
    st.info("Please upload both the policy wording and hospital bill PDFs.")
