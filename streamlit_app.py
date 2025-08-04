import streamlit as st
from openai import OpenAI
import re

from PIL import Image

# Load logo
logo = Image.open("logo.png")

# Inject heartbeat animation styling
st.markdown("""
    <style>
        .pulse {
            animation: pulse 2s infinite;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px;  /* Adjust size here */
            margin-top: -50px;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
    </style>
    <div class='pulse'>
""", unsafe_allow_html=True)


st.image(logo, width=120)


st.markdown("</div>", unsafe_allow_html=True)


PPLX_API_KEY = st.secrets["PPLX_API_KEY"]



# Initialize Perplexity LLM client
client = OpenAI(api_key=PPLX_API_KEY, base_url="https://api.perplexity.ai")



st.set_page_config(page_title="LeetCode Pattern Recognition", layout="wide")


st.markdown("""
<style>
html, body, .stApp {
    background: linear-gradient(
        rgba(10, 10, 28, 0.90),
        rgba(20, 20, 48, 0.93)
    ), url('https://images.unsplash.com/photo-1517433456452-f9633a875f6f?auto=format&fit=crop&w=2100&q=80')
    no-repeat center center fixed;
    background-size: cover;
    color: #e0e6ff !important;
}
.block-container, .main, .stApp {
    background: rgba(22,24,32,0.92) !important;
    border-radius: 1rem;
    margin-top: 2.5rem !important;
    color: #e0e6ff !important;
    box-shadow: 0 6px 24px rgba(15,14,45,0.12);
}
.stButton>button {
    border-radius: 7px;
    font-weight: 600;
    font-size: 18px;
    background: linear-gradient(90deg,#396afc 0%,#2948ff 100%);
    color: #fff;
    border: none;
    transition: all .21s;
}
.stButton>button:hover {
    background: linear-gradient(100deg,#2948ff 0%,#396afc 100%);
    color: #ffd86a;
}
.stExpanderHeader {
    font-size: 1.15rem !important;
    color: #ffde59 !important;
    font-weight: 500;
}
code, pre {
    background: #252a3a !important;
    color: #acd6ff !important;
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)


# Sidebar content
with st.sidebar:
    st.title("💻 ABOUT LEETPULSE")
    st.write(
        """LeetPulse is your intelligent coding companion designed to simplify LeetCode-style problems.
It provides:

Pattern and topic recognition

C++ template code with clear explanations

Brute-force and optimal solutions with step-by-step reasoning

A list of similar problems for further practice

Disclaimer: We strongly recommend attempting the problem on your own before using LeetPulse for guidance.
This tool is meant to support your learning, not replace your practice."""
    )
    st.markdown("---")
    st.info("Paste your LeetCode problem on the left panel and analyze.")



col1, col2 = st.columns([1, 2])


with col1:
    default_problem = """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."""
    problem = st.text_area("Enter LeetCode Problem Statement:", value=default_problem, height=300)


    analyze_btn = st.button("Analyze Problem")





def build_prompt(problem_statement: str) -> str:
    return f"""
You are a coding assistant expert specialized in algorithm patterns and LeetCode problems.


Given the following problem statement:


\"\"\"
{problem_statement}
\"\"\"


Please provide a thorough response with clearly labeled Markdown sections as below. Each section should be in C++ and include easy-to-understand explanations and step-by-step thinking.


# Pattern
Explain the main coding pattern(s) used for this problem.


# Topics
List and briefly explain the key algorithmic topics involved (e.g., arrays, sliding window).


# Template Code
Provide a C++ code template illustrating how to solve problems of this pattern type.
Include detailed comments and explain each step for clarity.


# Brute Force Solution
Provide a full C++ brute-force solution with inline comments and explain its time and space complexity. Include step-by-step logic.


# Optimal Solution
Provide a full optimized C++ solution with detailed comments, and explain how it improves over brute-force. Include time and space complexity analysis.


# Similar Questions
List some similar LeetCode problems or standard questions using this pattern.


Make sure each section is properly marked as a header (e.g., with `# Pattern`) so it can be parsed separately.
"""


def parse_sections(text: str):
    """Parse LLM response into labeled sections."""
    pattern = r"^# (.+?)\n([\s\S]*?)(?=^# |\Z)"
    matches = re.findall(pattern, text, re.MULTILINE)
    return {header.strip().lower(): content.strip() for header, content in matches}


@st.cache_data(show_spinner=False)
def query_perplexity_llm(problem_text: str) -> dict:
    prompt = build_prompt(problem_text)
    response = client.chat.completions.create(
        model="sonar-pro",  # valid Perplexity model
        messages=[
            {"role": "system", "content": "You are an expert coding assistant specializing in C++ LeetCode problems."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1800,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    return parse_sections(content)


# === Handle interactions and display output ===


if analyze_btn:
    if not problem.strip():
        st.warning("Please enter a LeetCode problem statement before analyzing.")
    else:
        st.info("Friendly Reminder: We know you're smart — try solving it yourself first before peeking at the solution! 😉")
        with st.spinner("⏳please wait"):
            try:
                sections = query_perplexity_llm(problem)
                st.session_state['sections'] = sections  # Persist data for UI interactivity
            except Exception as e:
                st.error(f"❌ Failed to get response from Perplexity LLM: {e}")
                st.stop()



sections = st.session_state.get('sections', None)


with col2:
    if sections:
        st.markdown("📤 RESULTS")


        if "pattern" in sections:
            with st.expander("Pattern Explanation", expanded=True):
                st.markdown(sections["pattern"])


        if "topics" in sections:
            with st.expander("Topics Covered"):
                st.markdown(sections["topics"])


        if "template code" in sections:
            with st.expander("C++ Template Code with Explanation"):
                st.code(sections["template code"], language="cpp")


        if "brute force solution" in sections:
            with st.expander("Brute Force Solution (C++) with Explanation"):
                st.code(sections["brute force solution"], language="cpp")


        if "optimal solution" in sections:
            with st.expander("Optimal Solution (C++) with Explanation"):
                st.code(sections["optimal solution"], language="cpp")
                # Download button for optimal code
                st.download_button(
                    label="Download Optimal Solution (solution.cpp)",
                    data=sections["optimal solution"],
                    file_name="solution.cpp",
                    mime="text/plain",
                )


        if "similar questions" in sections:
            with st.expander("Similar Questions on this Pattern"):
                st.markdown(sections["similar questions"])


    else:
        if analyze_btn:
            st.info("Waiting for analysis results...")
        else:
            st.info("Enter a problem statement and click 'Analyze Problem' to see results.")
