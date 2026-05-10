from typing import List, TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults


class GraphState(TypedDict):
    """
    The 'notebook' our bot uses to keep track of its work.
    """
    question: str
    generation: str
    web_search: str # "Yes" or "No"
    documents: List[str]

def retrieve(state):
    print("---RETRIEVING---")
    question = state["question"]
    
    # Mock data - in a real app, you'd query FAISS or Pinecone here
    documents = ["Python is a high-level programming language.", "LangGraph is used for AI agents."]
    return {"documents": documents, "question": question}

def grade_documents(state):
    print("---CHECKING RELEVANCE---")
    question = state["question"]
    documents = state["documents"]
    
    # Logic: If 'python' isn't in the docs but the user asked about it, 
    # we trigger web search.
    filtered_docs = []
    search = "No"
    
    for d in documents:
        if "python" in d.lower(): # Simplified logic for learning
            filtered_docs.append(d)
        else:
            search = "Yes" # If even one doc is bad, let's try the web
            
    return {"documents": filtered_docs, "question": question, "web_search": search}


def web_search(state):
    print("---WEB SEARCHING---")
    question = state["question"]
    documents = state["documents"]

    tool = TavilySearchResults(k=3)
    docs = tool.invoke({"query": question})
    
    # Format the web results to match our document list
    web_results = "\n".join([d["content"] for d in docs])
    documents.append(web_results)
    
    return {"documents": documents, "question": question}