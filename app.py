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

def decide_to_generate(state):
    """
    Determines whether to generate an answer or search the web.
    """
    print("---DECIDING NEXT STEP---")
    if state["web_search"] == "Yes":
        return "search"
    else:
        return "generate"

# We also need a 'Generate' node to actually give the final answer
def generate(state):
    print("---GENERATING FINAL ANSWER---")
    question = state["question"]
    documents = state["documents"]
    
    # In a real app, you'd pass 'documents' to an LLM here.
    # For now, let's just simulate the result.
    return {"generation": f"Based on {len(documents)} sources, here is the answer to: {question}"}

from langgraph.graph import END, StateGraph, START

# 1. Initialize the Graph with our State schema
workflow = StateGraph(GraphState)

# 2. Add all our Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("web_search", web_search)
workflow.add_node("generate", generate)

# 3. Build the Edges (The Flow)
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")

# 4. Add the Conditional Logic (The 'Corrective' part)
workflow.add_conditional_edges(
    "grade_documents", # After grading is done...
    decide_to_generate, # Run this function to decide where to go
    {
        "search": "web_search", # If it returns "search", go to web_search node
        "generate": "generate"   # If it returns "generate", go to generate node
    }
)

# 5. Connect the remaining paths to the end
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# 6. Compile the graph
app = workflow.compile()