import streamlit as st
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize model
model = ChatOpenAI()

# Create a state class
class BlogState(TypedDict):
    title: str
    outline: str
    content: str

# Node functions
def create_outline(state: BlogState) -> BlogState:
    # extract title from state
    title = state["title"]
    
    # call the model to create the outline
    prompt = f"Generate a detailed outline for a blog post about the topic: {title}"
    outline = model.invoke(prompt).content
    
    # update the state with the outline
    state["outline"] = outline
    return state

def create_blog(state: BlogState) -> BlogState:
    # extract title and outline from state
    title = state["title"]
    outline = state["outline"]
    
    # call the model to create the blog
    prompt = f"Write a detailed blog post about the topic: {title} with the following outline: {outline}"
    content = model.invoke(prompt).content
    
    # update the state with the blog
    state["content"] = content
    return state

# Create a graph
graph = StateGraph(BlogState)

# Create nodes
graph.add_node("create_outline", create_outline)
graph.add_node("create_blog", create_blog)

# Add edges
graph.add_edge(START, "create_outline")
graph.add_edge("create_outline", "create_blog")
graph.add_edge("create_blog", END)

# Compile the graph
workflow = graph.compile()

# Streamlit UI
st.set_page_config(page_title="AI Blog Generator", page_icon="✍️", layout="wide")

st.title("✍️ AI Blog Generator")
st.markdown("LangGraph Prompt Chaining ke saath blog generate karein!")

st.divider()

title = st.text_input("📝 Blog ka Title likhein:", placeholder="e.g., Rise of AI in 2026")

if st.button("🚀 Blog Generate Karein", type="primary"):
    if title.strip() == "":
        st.error("❌ Pehle title likhein!")
    else:
        with st.spinner("⏳ Blog generate ho raha hai..."):
            initial_state = {"title": title, "outline": "", "content": ""}
            final_state = workflow.invoke(initial_state)
        
        st.success("✅ Blog generate ho gaya!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Outline")
            st.markdown(final_state["outline"])
        
        with col2:
            st.subheader("📄 Blog Content")
            st.markdown(final_state["content"])

