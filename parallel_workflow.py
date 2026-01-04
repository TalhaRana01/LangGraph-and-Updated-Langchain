# =============================================================================
# SECTION 2: BASIC IMPORTS
# =============================================================================

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from typing_extensions import TypedDict as ExtTypedDict
from operator import add
import operator



# =============================================================================
# SECTION 4: EXAMPLE 2 - PARALLEL WORKFLOW
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 2: PARALLEL WORKFLOW")
print("="*80)

class ParallelState(TypedDict):
    """State for parallel processing"""
    input_value: int
    squared: int
    cubed: int
    doubled: int
    summary: str

def square_node(state: ParallelState) -> ParallelState:
    """Calculate square"""
    print(f"  -> Calculating square...")
    return {"squared": state["input_value"] ** 2}

def cube_node(state: ParallelState) -> ParallelState:
    """Calculate cube"""
    print(f"  -> Calculating cube...")
    return {"cubed": state["input_value"] ** 3}

def double_node(state: ParallelState) -> ParallelState:
    """Calculate double"""
    print(f"  -> Calculating double...")
    return {"doubled": state["input_value"] * 2}

# def summary_node(state: ParallelState) -> ParallelState:
#     """Create summary"""
#     print(f"  -> Creating summary...")
#     summary = (
#        f"Input: {state['input_value']}\n"
#        f"Square: {state['squared']}\n"
#        f"Cube: {state['cubed']}\n"
#        f"Double: {state['doubled']}\n"
#     )
#     return {"summary": summary}


def summary_node(state: ParallelState) -> ParallelState:
  """Create summary"""
  print(f"  -> Creating summary...")
  
  summary = {
    "input_value": state["input_value"],
    "squared": state["squared"],
    "cubed": state["cubed"],
    "doubled": state["doubled"]
  }
  return {"summary": summary}


# Create parallel graph
parallel_graph = StateGraph(ParallelState)

parallel_graph.add_node("square", square_node)
parallel_graph.add_node("cube", cube_node)
parallel_graph.add_node("double", double_node)
parallel_graph.add_node("summary", summary_node)

# Parallel edges from START
parallel_graph.add_edge(START, "square")
parallel_graph.add_edge(START, "cube")
parallel_graph.add_edge(START, "double")

# All converge to summary
parallel_graph.add_edge("square", "summary")
parallel_graph.add_edge("cube", "summary")
parallel_graph.add_edge("double", "summary")
parallel_graph.add_edge("summary", END)

# Compile and execute
parallel_workflow = parallel_graph.compile()
result = parallel_workflow.invoke({"input_value": 5})
print(f"\n✅ Result: {result}")