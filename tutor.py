import os
import streamlit as st
from google import genai
from google.genai import types
import time
from datetime import datetime
import json
from pydantic import BaseModel

def save_evaluation_as_json(file_name, evaluation_summary):
    # Define the base directory and evaluation directory
    base_dir = "My_Knowledge"
    evaluations_dir = os.path.join(base_dir, "evaluations")
    os.makedirs(evaluations_dir, exist_ok=True)
    
    # Create a folder named 'abc_evaluation' for 'abc.txt'
    evaluation_folder_name = f"{os.path.splitext(file_name)[0]}_evaluation"
    evaluation_folder_path = os.path.join(evaluations_dir, evaluation_folder_name)
    os.makedirs(evaluation_folder_path, exist_ok=True)
    
    # Generate a unique filename using the current datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.json"
    json_file_path = os.path.join(evaluation_folder_path, json_file_name)
    
    # Save the evaluation summary as a JSON file
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(evaluation_summary, json_file, ensure_ascii=False, indent=4)
    
    return json_file_path

# Page configuration
st.set_page_config(
    page_title="Knowledge Evaluator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         color: #1E3A8A;
#         margin-bottom: 1rem;
#     }
#     .sub-header {
#         font-size: 1.8rem;
#         color: #2563EB;
#         margin-top: 2rem;
#     }
#     .file-content {
#         border-radius: 10px;
#         border: 1px solid #E5E7EB;
#         padding: 10px;
#         background-color: #F9FAFB;
#     }
#     .stProgress > div > div {
#         background-color: #2563EB;
#     }
#     .evaluation-box {
#         border-left: 4px solid #2563EB;
#         padding-left: 20px;
#         margin-top: 20px;
#         background-color: #F0F9FF;
#         padding: 20px;
#         border-radius: 5px;
#     }
#     .stButton>button {
#         background-color: #2563EB;
#         color: white;
#         border-radius: 5px;
#         padding: 10px 20px;
#         font-weight: bold;
#     }
#     .stButton>button:hover {
#         background-color: #1E40AF;
#     }
#     .sidebar-info {
#         padding: 10px;
#         background-color: #F0F9FF;
#         border-radius: 5px;
#         margin-top: 20px;
#     }
#     .feedback-section {
#         margin-top: 15px;
#         padding: 15px;
#         border-radius: 5px;
#     }
#     .positive-feedback {
#         background-color: #ECFDF5;
#         border-left: 4px solid #10B981;
#     }
#     .negative-feedback {
#         background-color: #FEF2F2;
#         border-left: 4px solid #EF4444;
#     }
#     .recommendations {
#         background-color: #EFF6FF;
#         border-left: 4px solid #3B82F6;
#     }
# </style>
# """, unsafe_allow_html=True)
# Custom CSS for fully colored sections with text
st.markdown("""
<style>
    .feedback-section {
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        color: #1F2937; /* Text color */
        font-weight: bold;
    }
    .positive-feedback {
        background-color: #ECFDF5; /* Light green */
        border: 2px solid #10B981; /* Darker green */
    }
    .positive-feedback::before {
        content: "✅ What's Right";
        display: block;
        margin-bottom: 10px;
        font-size: 1.2rem;
        color: #047857; /* Dark green text */
    }
    .negative-feedback {
        background-color: #FEF2F2; /* Light red */
        border: 2px solid #EF4444; /* Darker red */
    }
    .negative-feedback::before {
        content: "❌ What's Wrong";
        display: block;
        margin-bottom: 10px;
        font-size: 1.2rem;
        color: #B91C1C; /* Dark red text */
    }
    .recommendations {
        background-color: #EFF6FF; /* Light blue */
        border: 2px solid #3B82F6; /* Darker blue */
    }
    .recommendations::before {
        content: "💡 Recommendations";
        display: block;
        margin-bottom: 10px;
        font-size: 1.2rem;
        color: #1D4ED8; /* Dark blue text */
    }
</style>
""", unsafe_allow_html=True)





# Initialize the Google GenAI client using your API key
api_key = 'Enter your Google API key'
if not api_key:
    st.error("Please set your GOOGLE_API_KEY environment variable.")
    st.stop()

client = genai.Client(api_key=api_key)

# App header
st.markdown("<h1 class='main-header'>Knowledge Evaluator 🧠</h1>", unsafe_allow_html=True)
st.markdown("Upload your knowledge files and get AI-powered feedback on your understanding.")

# Define the folder where your knowledge files are stored
KNOWLEDGE_FOLDER = "My_Knowledge"

# Create folder if it doesn't exist
os.makedirs(KNOWLEDGE_FOLDER, exist_ok=True)

# Sidebar with file management
with st.sidebar:
    st.markdown("## 📁 Knowledge Files")
    
    # Input for new file creation
    new_file_name = st.text_input("Enter new file name (with .txt extension)")
    new_file_content =''
    # new_file_content = st.text_area("Enter initial content for the new file (optional)", height=100)

    
    if st.button("Create New File"):
        if new_file_name:
            if not new_file_name.endswith(".txt"):
                st.error("File name must end with .txt")
            else:
                file_path = os.path.join(KNOWLEDGE_FOLDER, new_file_name)
                if os.path.exists(file_path):
                    st.error("File already exists. Please choose a different name.")
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_file_content)
                    st.success(f"File '{new_file_name}' created successfully!")
                    st.rerun()  # Refresh to show the new file in the list
        else:
            st.error("Please enter a file name.")
    
    # Get list of text files in the folder
    try:
        files = [f for f in os.listdir(KNOWLEDGE_FOLDER) if f.endswith(".txt")]
        files.sort()  # Sort files alphabetically
    except FileNotFoundError:
        st.error(f"Folder '{KNOWLEDGE_FOLDER}' not found.")
        st.stop()
    
    if not files:
        st.info("No knowledge files found. Please create a new file.")
    else:
        selected_file = st.selectbox("Select a topic file", files)
        
        # Display file info
        if selected_file:
            file_path = os.path.join(KNOWLEDGE_FOLDER, selected_file)
            file_stats = os.stat(file_path)
            last_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
            
            st.markdown("<div class='sidebar-info'>", unsafe_allow_html=True)
            st.markdown(f"**File:** {selected_file}")
            st.markdown(f"**Size:** {file_stats.st_size/1024:.1f} KB")
            st.markdown(f"**Last modified:** {last_modified}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Delete File"):
                os.remove(file_path)
                st.success(f"File '{selected_file}' deleted successfully!")
                st.rerun()  # Refresh to show the updated list of files



# Main content area with tabs
tab1, tab2 = st.tabs(["Content Review", "Evaluation History"])



class eval_results(BaseModel):
  whats_right: str
  whats_wrong: str
  recommendations: str

with tab1:
    # Read and display the content of the selected file
    if 'selected_file' in locals() and selected_file:
        file_path = os.path.join(KNOWLEDGE_FOLDER, selected_file)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        st.markdown(f"<h2 class='sub-header'>📝 {selected_file}</h2>", unsafe_allow_html=True)
        
        # Text editor for content
        edited_content = st.text_area("Edit your knowledge content if needed", value=content, height=300, key="content_editor")
        
        # Save edited content
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Save Changes") and edited_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(edited_content)
                st.success("Content saved successfully!")
                content = edited_content
        
        # Model selection
        model_options = {
            "gemini-2.0-flash": "Gemini 2.0 Flash (Fastest)",
            "gemini-2.0-pro": "Gemini 2.0 Pro (Balanced)",
            "gemini-2.0-ultra": "Gemini 2.0 Ultra (Most detailed)"
        }
        
        col1, col2 = st.columns([1, 1])
        with col1:
            selected_model = st.selectbox(
                "Select evaluation model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=0
            )
        
        with col2:
            evaluation_focus = st.radio(
                "Evaluation focus",
                options=["General understanding", "Conceptual accuracy", "Academic rigor"],
                horizontal=True
            )
        
        # Evaluate button
        if st.button("Evaluate Content"):
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(1, 101):
                # Update progress bar
                progress_bar.progress(i)
                
                if i < 30:
                    status_text.text("Analyzing content structure...")
                elif i < 60:
                    status_text.text("Identifying key concepts...")
                elif i < 90:
                    status_text.text("Generating detailed feedback...")
                else:
                    status_text.text("Finalizing evaluation...")
                
                # Simulate processing time
                time.sleep(0.05)
            
            status_text.empty()

            # Construct the evaluation prompt based on focus
            prompt_additions = {
                "General understanding": "Focus on overall grasp of concepts.",
                "Conceptual accuracy": "Focus deeply on precision of technical terms and relationships between concepts.",
                "Academic rigor": "Evaluate with academic standards in mind, highlighting scholarly accuracy."
            }
            
            prompt = (
                f"Evaluate the following content with focus on {evaluation_focus}. {prompt_additions[evaluation_focus]}\n\n"
                "Provide your feedback in these three clearly separated sections:\n\n"
                "1. What's Right: Highlight the aspects that demonstrate correct understanding.\n"
                "2. What's Wrong: Identify any misconceptions or errors.\n"
                "3. Recommendations: Suggest specific topics or areas to focus on for improvement.\n\n"
                "Content:\n" + edited_content
            )

            # Call the selected Gemini model
            try:
                response = client.models.generate_content(
                    model=selected_model,
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': eval_results,
    }
                    # config=types.GenerateContentConfig(
                    #     max_output_tokens=800,
                    #     temperature=0.2
                    # )
                )
                
                evaluation = response.text
                
                # Store the evaluation in session state
                if 'evaluation_history' not in st.session_state:
                    st.session_state.evaluation_history = []
                
                st.session_state.evaluation_history.append({
                    'file': selected_file,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'model': selected_model,
                    'focus': evaluation_focus,
                    'evaluation': evaluation
                })
                
                # Extract the three sections
                # sections = evaluation.split('\n\n')
                # whats_right = ""
                # whats_wrong = ""
                # recommendations = ""
                

                # for section in sections:
                #     if section.lower().startswith("what's right") or section.lower().startswith("1. what's right"):
                #         whats_right = section 
                #     elif section.lower().startswith("what's wrong") or section.lower().startswith("2. what's wrong"):
                #         whats_wrong = section
                #     elif section.lower().startswith("recommendations") or section.lower().startswith("3. recommendations"):
                #         recommendations = section
                # evaluation_summary = {"What's Right": whats_right,
                #                       "What's Wrong": whats_wrong,
                #                       "Recommendations": recommendations
                #                       }
                evaluation_summary = json.loads(evaluation)
                whats_right = evaluation_summary['whats_right']
                whats_wrong = evaluation_summary['whats_wrong']
                recommendations = evaluation_summary['recommendations']
                save_evaluation_as_json(selected_file,evaluation_summary)
                
                # Display the evaluation results in a formatted way
                st.markdown("<h3 class='sub-header'>Evaluation Results</h3>", unsafe_allow_html=True)
                
                if whats_right:
                    st.markdown("<div class='feedback-section positive-feedback'>", unsafe_allow_html=True)
                    st.markdown(whats_right)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if whats_wrong:
                    st.markdown("<div class='feedback-section negative-feedback'>", unsafe_allow_html=True)
                    st.markdown(whats_wrong)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if recommendations:
                    st.markdown("<div class='feedback-section recommendations'>", unsafe_allow_html=True)
                    st.markdown(recommendations)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # If no proper sections were found, display the raw evaluation
                if not (whats_right or whats_wrong or recommendations):
                    st.markdown("<div class='evaluation-box'>", unsafe_allow_html=True)
                    st.markdown(evaluation)
                    st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error during evaluation: {e}")
    else:
        st.info("Please select a knowledge file from the sidebar to review.")

EVALUATIONS_FOLDER = os.path.join("My_Knowledge", "evaluations")

with tab2:
    st.markdown("<h2 class='sub-header'>📊 Evaluation History</h2>", unsafe_allow_html=True)
    
    # Dynamically determine the evaluation subfolder
    if 'selected_file' in locals() and selected_file:
        eval_subfolder = os.path.join(EVALUATIONS_FOLDER, selected_file.split(".")[0] + "_evaluation")
        os.makedirs(eval_subfolder, exist_ok=True)  # Ensure the subfolder exists
        
        try:
            eval_files = [f for f in os.listdir(eval_subfolder) if f.endswith(".json")]
            eval_files.sort()  # Sort files alphabetically
        except FileNotFoundError:
            st.error(f"Folder '{eval_subfolder}' not found.")
            eval_files = []
        
        if not eval_files:
            st.info("No evaluation files found in the selected folder.")
        else:
            selected_eval_file = st.selectbox("Select an evaluation file", eval_files)
            
            if selected_eval_file:
                eval_file_path = os.path.join(eval_subfolder, selected_eval_file)
                
                # Display file info
                file_stats = os.stat(eval_file_path)
                last_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                st.markdown("<div class='sidebar-info'>", unsafe_allow_html=True)
                st.markdown(f"**File:** {selected_eval_file}")
                st.markdown(f"**Size:** {file_stats.st_size/1024:.1f} KB")
                st.markdown(f"**Last modified:** {last_modified}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Load and display JSON content
                try:
                    with open(eval_file_path, "r", encoding="utf-8") as f:
                        eval_data = json.load(f)
                    
                    st.json(eval_data, expanded=True)
                    
                except json.JSONDecodeError:
                    st.error(f"Error decoding JSON content in file '{selected_eval_file}'.")
                except Exception as e:
                    st.error(f"Error reading file '{selected_eval_file}': {e}")
    else:
        st.info("Please select a knowledge file from the sidebar to load its evaluations.")


# Footer
st.markdown("---")
st.markdown("Knowledge Evaluator App |Powered by Google Gemini 2.0 |  Made with ❤️ using Streamlit | Vaarrun |")