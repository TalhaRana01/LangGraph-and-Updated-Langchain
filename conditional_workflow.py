# =============================================================================
# SECTION 2: BASIC IMPORTS
# =============================================================================

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from typing_extensions import TypedDict as ExtTypedDict
from operator import add
import operator



# =============================================================================
# SECTION 5: EXAMPLE 3 - CONDITIONAL WORKFLOW
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 3: CONDITIONAL WORKFLOW (ROUTING)")
print("="*80)

class ConditionalState(TypedDict):
    """State with conditional routing"""
    number: int
    category: str
    result: str

def categorize_node(state: ConditionalState) -> ConditionalState:
    """Categorize the number"""
    print(f"  -> Categorizing number: {state['number']}")
    if state["number"] < 0:
        category = "negative"
    elif state["number"] == 0:
        category = "zero"
    else:
        category = "positive"
    return {"category": category}

def handle_negative(state: ConditionalState) -> ConditionalState:
    """Handle negative numbers"""
    print(f"  -> Handling negative number")
    return {"result": f"{state['number']} is negative"}

def handle_zero(state: ConditionalState) -> ConditionalState:
    """Handle zero"""
    print(f"  -> Handling zero")
    return {"result": "Number is zero"}

def handle_positive(state: ConditionalState) -> ConditionalState:
    """Handle positive numbers"""
    print(f"  -> Handling positive number")
    return {"result": f"{state['number']} is positive"}

# Router function
def route_by_category(state: ConditionalState) -> Literal["negative", "zero", "positive"]:
    """Route based on category"""
    print(f"  -> Routing to: {state['category']}")
    return state["category"]

# Create conditional graph
conditional_graph = StateGraph(ConditionalState)
conditional_graph.add_node("categorize", categorize_node)
conditional_graph.add_node("negative", handle_negative)
conditional_graph.add_node("zero", handle_zero)
conditional_graph.add_node("positive", handle_positive)

# Add edges
conditional_graph.add_edge(START, "categorize")

# Conditional edge based on category
conditional_graph.add_conditional_edges(
    "categorize",
    route_by_category,
    {
        "negative": "negative",
        "zero": "zero",
        "positive": "positive"
    }
)

# All paths lead to END
conditional_graph.add_edge("negative", END)
conditional_graph.add_edge("zero", END)
conditional_graph.add_edge("positive", END)

# Compile and test
conditional_workflow = conditional_graph.compile()

print("\nTest 1: Positive number")
result1 = conditional_workflow.invoke({"number": 42})
print(f"✅ Result: {result1}")

print("\nTest 2: Negative number")
result2 = conditional_workflow.invoke({"number": -10})
print(f"✅ Result: {result2}")

print("\nTest 3: Zero")
result3 = conditional_workflow.invoke({"number": 0})
print(f"✅ Result: {result3}")