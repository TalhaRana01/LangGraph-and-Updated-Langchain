# =============================================================================
# SECTION 2: BASIC IMPORTS
# =============================================================================

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from typing_extensions import TypedDict as ExtTypedDict
from operator import add
import operator

# =============================================================================
# SECTION 3: EXAMPLE 1 - SIMPLE LINEAR WORKFLOW
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 1: SIMPLE LINEAR WORKFLOW")
print("="*80)

# State definition
class SimpleState(TypedDict):
    """Simple state with a message"""
    message: str
    count: int

# Node functions
def node_a(state: SimpleState) -> SimpleState:
    """First node - adds greeting"""
    print(f"  -> Node A executing...")
    return {
        "message": state["message"] + " Hello",
        "count": state["count"] + 1
    }

def node_b(state: SimpleState) -> SimpleState:
    """Second node - adds name"""
    print(f"  -> Node B executing...")
    return {
        "message": state["message"] + " from LangGraph!",
        "count": state["count"] + 1
    }

# Create graph
simple_graph = StateGraph(SimpleState)
simple_graph.add_node("a", node_a)
simple_graph.add_node("b", node_b)

# Add edges: START → a → b → END
simple_graph.add_edge(START, "a")
simple_graph.add_edge("a", "b")
simple_graph.add_edge("b", END)

# Compile
simple_workflow = simple_graph.compile()

# Execute
initial_state = {"message": "", "count": 0}
result = simple_workflow.invoke(initial_state)
print(f"\n✅ Result: {result}")