import streamlit as st

# Configure page
st.set_page_config(
    page_title="🏥 Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# State management
if "page" not in st.session_state:
    st.session_state.page = "home"

def set_page(page_name):
    st.session_state.page = page_name

# Dark theme CSS
def load_light_css():
    st.markdown("""
        <style>
            /* Main background */
            .stApp {
                background-color: #f8f9fa;
                color: #212529;
            }

            /* Text colors */
            h1, h2, h3, h4, h5, h6, p, div, span {
                color: #212529 !important;
            }

            /* Cards */
            .feature-card {
                background: #ffffff !important;
                border-radius: 12px !important;
                padding: 2rem !important;
                border: 1px solid #ddd !important;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                height: 100%;
            }

            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
                border: 1px solid #8a2be2 !important;
            }

            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #8a2be2;
            }

            .feature-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }

            .feature-desc {
                color: #555555;
                line-height: 1.6;
            }

            /* Buttons */
            .stButton>button {
                background-color: #8a2be2 !important;
                color: white !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                border: none !important;
                padding: 0.5rem 1.5rem !important;
                transition: all 0.3s ease !important;
            }

            .stButton>button:hover {
                background-color: #6a1bb0 !important;
                transform: scale(1.05);
                box-shadow: 0 0 10px rgba(138, 43, 226, 0.3);
            }

            /* Back button */
            .back-btn {
                margin-bottom: 2rem;
            }

            /* Header */
            .main-header {
                text-align: center;
                margin-bottom: 3rem;
            }

            .main-header h1 {
                font-size: 3rem;
                background: linear-gradient(90deg, #8a2be2, #00f2ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }

            .main-header p {
                color: #666666;
                font-size: 1.1rem;
                max-width: 600px;
                margin: 0 auto;
            }

            /* Footer */
            .main-footer {
                text-align: center;
                margin-top: 4rem;
                padding: 2rem 0;
                color: #999999;
                border-top: 1px solid #ddd;
            }
        </style>
    """, unsafe_allow_html=True)

# Home Page
def show_home():
    load_light_css()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🏥 Health Assistant</h1>
            <p>Advanced medical tools powered by AI to help you understand your health data</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Report Analyzer</div>
                <div class="feature-desc">
                    Upload your medical reports, lab results, or scans to receive 
                    clear explanations and personalized insights about your health metrics.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Report Analyzer", key="analyzer_btn", use_container_width=True):
            st.write("⏳ Switching to analyzer page...")
            set_page("analyzer")
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Medical Chatbot</div>
                <div class="feature-desc">
                    Get answers to your health questions from our AI assistant trained 
                    on medical literature. Always consult a doctor for serious concerns.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Medical Chatbot", key="chatbot_btn", use_container_width=True):
            st.write("⏳ Switching to chatbot page...")
            set_page("chatbot")
    # Footer
    st.markdown("""
        <div class="main-footer">
            | Not for medical emergencies | Always consult a doctor for serious concerns
        </div>
    """, unsafe_allow_html=True)

# Report Analyzer Page
def show_analyzer():
    load_light_css()
    st.button("← Back to Home", key="back_analyzer", on_click=lambda: set_page("home"))
    
    # Simply call  hack.py module
    try:
        import hack
        hack.run()  
    except Exception as e:
        st.error(f"Error loading Report Analyzer: {str(e)}")

# Chatbot Page
def show_chatbot():
    load_light_css()
    st.button("← Back to Home", key="back_chatbot", on_click=lambda: set_page("home"))
    
    # Simply call  medibot.py module
    try:
        import medibot
        medibot.run()  
    except Exception as e:
        st.error(f"Error loading Medical Chatbot: {str(e)}")

# Page routing
if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "analyzer":
    show_analyzer()
elif st.session_state.page == "chatbot":
    show_chatbot()