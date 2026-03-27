import streamlit as st
import os
from dotenv import load_dotenv
from html_templates import css, bot_template, user_template
from utils import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain
from database import init_db, add_document, get_documents, delete_document, clear_all_documents
from datetime import datetime
import json

DOCS_DIR = "docs"
HISTORY_FILE = "chat_history.json"

if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

def save_chat_history():
    """Save chat history to file"""
    if st.session_state.chat_history:
        history_data = []
        for msg in st.session_state.chat_history:
            history_data.append({
                'content': msg.content,
                'is_user': msg.is_user,
                'timestamp': datetime.now().isoformat()
            })
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2)

def export_chat_to_txt():
    """Export chat history to TXT file"""
    if not st.session_state.chat_history:
        return None
    
    content = "Chat with Your Notes - Conversation History\n"
    content += "=" * 50 + "\n\n"
    
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            content += f"Q: {message.content}\n\n"
        else:
            content += f"A: {message.content}\n\n"
            content += "-" * 50 + "\n\n"
    
    return content

def get_document_stats():
    """Get statistics about uploaded documents"""
    documents = get_documents()
    if not documents:
        return None
    
    total_docs = len(documents)
    total_size = 0
    
    for doc in documents:
        filepath = doc[2]
        if os.path.exists(filepath):
            total_size += os.path.getsize(filepath)
    
    return {
        'total_docs': total_docs,
        'total_size_mb': round(total_size / (1024 * 1024), 2)
    }

def handle_userinput(user_question):
    if st.session_state.conversation:
        with st.spinner("Thinking..."):
            response = st.session_state.conversation({'question': user_question})
            st.session_state.chat_history = response['chat_history']
            save_chat_history()

        # Only show last 5 question-answer pairs (10 messages total)
        recent_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
        
        for i, message in enumerate(recent_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                # Add copy button for answers
                col1, col2 = st.columns([0.95, 0.05])
                with col1:
                    st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                with col2:
                    if st.button("📋", key=f"copy_{i}", help="Copy answer"):
                        st.code(message.content, language=None)
    else:
        st.warning("Please process your documents first.")

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def main():
    load_dotenv()
    init_db()
    
    st.set_page_config(
        page_title="Chat with Your Notes", 
        page_icon=":books:", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.write(css, unsafe_allow_html=True)

    # Initialize session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "huggingface_api_token" not in st.session_state:
        st.session_state.huggingface_api_token = "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"
    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = True

    # Header with stats
    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
    with col_h1:
        st.title("📚 Chat with Your Notes")
    with col_h2:
        stats = get_document_stats()
        if stats:
            st.metric("Documents", stats['total_docs'])
    with col_h3:
        if stats:
            st.metric("Total Size", f"{stats['total_size_mb']} MB")

    st.markdown("---")
    
    with st.sidebar:
        st.subheader("⚙️ Configuration")
        api_token = st.text_input(
            "HuggingFace API Token", 
            value=st.session_state.huggingface_api_token, 
            type="password", 
            help="Get your token from huggingface.co/settings/tokens"
        )
        if api_token:
            st.session_state.huggingface_api_token = api_token

        st.markdown("---")
        st.subheader("📁 Library Management")
        
        # File uploader with multiple formats
        uploaded_files = st.file_uploader(
            "Upload documents", 
            accept_multiple_files=True, 
            type=['pdf', 'txt'],
            help="Supported formats: PDF, TXT"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = save_uploaded_file(uploaded_file)
                add_document(uploaded_file.name, file_path)
            st.success(f"✅ Uploaded {len(uploaded_files)} file(s)")
            st.rerun()

        st.markdown("---")
        st.subheader("📚 Your Library")
        documents = get_documents()
        
        if documents:
            # Search in library
            search_term = st.text_input("🔍 Search documents", "")
            
            filtered_docs = documents
            if search_term:
                filtered_docs = [doc for doc in documents if search_term.lower() in doc[1].lower()]
            
            for doc in filtered_docs:
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.text(doc[1][:40] + "..." if len(doc[1]) > 40 else doc[1])
                with col2:
                    if st.button("❌", key=f"del_{doc[0]}", help="Delete"):
                        delete_document(doc[0])
                        st.rerun()
            
            st.markdown("---")
            
            # Action buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ Clear All", use_container_width=True):
                    clear_all_documents()
                    st.session_state.conversation = None
                    st.session_state.chat_history = None
                    # Clear cache
                    if os.path.exists("vectorstore.pkl"):
                        os.remove("vectorstore.pkl")
                    st.success("Library cleared!")
                    st.rerun()
            
            with col_btn2:
                # Export library list
                if st.button("📥 Export List", use_container_width=True):
                    doc_list = "\n".join([f"{i+1}. {doc[1]}" for i, doc in enumerate(documents)])
                    st.download_button(
                        "Download List",
                        doc_list,
                        "document_list.txt",
                        "text/plain"
                    )
        else:
            st.info("No documents in library.")

        st.markdown("---")
        st.subheader("🚀 Actions")
        
        if st.button("⚡ Process Library", use_container_width=True, type="primary"):
            if not st.session_state.huggingface_api_token:
                st.error("Please enter a HuggingFace API Token.")
            elif not documents:
                st.error("Library is empty.")
            else:
                with st.spinner("Processing library..."):
                    doc_paths = [doc[2] for doc in documents]
                    
                    raw_text = get_pdf_text(doc_paths)
                    text_chunks = get_text_chunks(raw_text)
                    vectorstore = get_vectorstore(text_chunks, st.session_state.huggingface_api_token)
                    st.session_state.conversation = get_conversation_chain(vectorstore, st.session_state.huggingface_api_token)
                    
                    st.success("✅ Library processed! Ask questions now.")

        # Export chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("💾 Export Chat")
            
            chat_txt = export_chat_to_txt()
            if chat_txt:
                st.download_button(
                    "📄 Download as TXT",
                    chat_txt,
                    f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "text/plain",
                    use_container_width=True
                )

    # Main chat area
    st.subheader("💬 Ask Questions")
    
    # Quick suggestions
    if st.session_state.show_suggestions and st.session_state.conversation:
        st.markdown("**Quick Suggestions:**")
        suggestions = [
            "Summarize the main points",
            "What are the key takeaways?",
            "Explain this in simple terms",
            "What are the important dates mentioned?"
        ]
        
        cols = st.columns(4)
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"sug_{i}"):
                    st.session_state.current_question = suggestion
                    st.rerun()
    
    # Question input
    user_question = st.text_input(
        "Ask a question about your documents:",
        value=st.session_state.get("current_question", ""),
        key="question_input"
    )
    
    # Clear the current_question after using it
    if "current_question" in st.session_state:
        del st.session_state.current_question
    
    if user_question:
        handle_userinput(user_question)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        💡 Tip: Upload multiple documents, process them, and ask questions to get AI-powered answers!
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
