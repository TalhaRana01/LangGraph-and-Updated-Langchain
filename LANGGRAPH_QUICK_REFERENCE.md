# 🚀 LangGraph Quick Reference Cheat Sheet

**Roman Urdu mein - Jaldi se reference ke liye**

---

## 📦 Installation

```bash
pip install langgraph
```

---

## 🎯 Basic Template

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. State define karen
class MyState(TypedDict):
    field: str

# 2. Node function banayein
def my_node(state: MyState) -> MyState:
    return {"field": "new_value"}

# 3. Graph banayein
graph = StateGraph(MyState)
graph.add_node("node_name", my_node)
graph.add_edge(START, "node_name")
graph.add_edge("node_name", END)

# 4. Compile aur run karen
workflow = graph.compile()
result = workflow.invoke({"field": "initial"})
```

---

## 🔑 Core Components

### State Definition

```python
from typing import TypedDict, Annotated
from operator import add

class MyState(TypedDict):
    # Simple fields
    name: str
    count: int
    active: bool
    
    # List with accumulation
    messages: Annotated[list[str], add]
    
    # Complex types
    metadata: dict
    items: list[dict]
```

### Node Function

```python
def process_node(state: MyState) -> MyState:
    """
    Input: current state
    Output: dictionary with updates
    """
    # Process kuch bhi
    result = state["count"] + 1
    
    # Return updates only
    return {
        "count": result,
        "active": True
    }
```

---

## 🔗 Edges

### Normal Edge
```python
# Direct connection
graph.add_edge("node_a", "node_b")
```

### Conditional Edge
```python
from typing import Literal

def router(state: MyState) -> Literal["path_a", "path_b"]:
    if state["count"] > 10:
        return "path_a"
    return "path_b"

graph.add_conditional_edges(
    "source_node",
    router,
    {
        "path_a": "node_a",
        "path_b": "node_b"
    }
)
```

### Parallel Edges
```python
# Yeh sab parallel mein run honge
graph.add_edge(START, "task1")
graph.add_edge(START, "task2")
graph.add_edge(START, "task3")
```

---

## 🎨 Common Patterns

### Pattern 1: Linear Pipeline
```python
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)
```

**Flow:**
```
START -> step1 -> step2 -> step3 -> END
```

---

### Pattern 2: Parallel Processing
```python
# Fan-out
graph.add_edge(START, "task1")
graph.add_edge(START, "task2")
graph.add_edge(START, "task3")

# Fan-in
graph.add_edge("task1", "combine")
graph.add_edge("task2", "combine")
graph.add_edge("task3", "combine")
graph.add_edge("combine", END)
```

**Flow:**
```
        -> task1 ->
START ->-> task2 ->-> combine -> END
        -> task3 ->
```

---

### Pattern 3: Conditional Routing
```python
def decide(state: MyState) -> Literal["yes", "no"]:
    return "yes" if state["value"] > 0 else "no"

graph.add_edge(START, "check")
graph.add_conditional_edges(
    "check",
    decide,
    {
        "yes": "handle_yes",
        "no": "handle_no"
    }
)
graph.add_edge("handle_yes", END)
graph.add_edge("handle_no", END)
```

**Flow:**
```
              -> handle_yes -> END
START -> check
              -> handle_no -> END
```

---

### Pattern 4: Loop/Cycle
```python
def should_continue(state: MyState) -> Literal["continue", "end"]:
    if state["counter"] < state["max"]:
        return "continue"
    return "end"

graph.add_edge(START, "process")
graph.add_conditional_edges(
    "process",
    should_continue,
    {
        "continue": "process",  # Loop back!
        "end": END
    }
)
```

**Flow:**
```
START -> process <-|
           |        |
         [check]    |
           |        |
      continue? ----+
           |
          END
```

---

## 🛡️ Error Handling

### Try-Catch Pattern
```python
def safe_node(state: MyState) -> MyState:
    try:
        result = risky_operation(state["data"])
        return {
            "result": result,
            "status": "success",
            "error": None
        }
    except ValueError as e:
        return {
            "result": None,
            "status": "error",
            "error": str(e)
        }
    except Exception as e:
        return {
            "result": None,
            "status": "error",
            "error": f"Unexpected: {str(e)}"
        }
```

### Error Routing
```python
def route_by_status(state: MyState) -> Literal["success", "error"]:
    return state["status"]

graph.add_conditional_edges(
    "risky_operation",
    route_by_status,
    {
        "success": "continue_processing",
        "error": "error_handler"
    }
)
```

---

## 📊 State Management

### Simple State
```python
class SimpleState(TypedDict):
    value: int

# Update overwrites
def update(state: SimpleState) -> SimpleState:
    return {"value": 42}  # Overwrites previous value
```

### Accumulator State
```python
from typing import Annotated
from operator import add

class AccState(TypedDict):
    items: Annotated[list[str], add]

# Updates accumulate
def add_item(state: AccState) -> AccState:
    return {"items": ["new_item"]}  # Adds to list, doesn't overwrite
```

---

## 🔍 Debugging

### Visualize Graph
```python
# Text representation
print(workflow.get_graph())

# Mermaid diagram (if available)
from IPython.display import Image, display
display(Image(workflow.get_graph().draw_mermaid_png()))
```

### Add Logging
```python
def debug_node(state: MyState) -> MyState:
    print(f"Current state: {state}")
    
    # Your logic here
    result = process(state)
    
    print(f"After processing: {result}")
    return result
```

### Step-by-Step Execution
```python
# Stream results to see each step
for chunk in workflow.stream(initial_state):
    print(f"Step: {chunk}")
```

---

## ✅ Best Practices

### DO ✅
```python
# Clear state definition
class GoodState(TypedDict):
    user_id: str
    count: int
    messages: Annotated[list[str], add]

# Focused nodes
def validate_email(state: GoodState) -> GoodState:
    """Does one thing well"""
    is_valid = "@" in state.get("email", "")
    return {"email_valid": is_valid}

# Error handling
def safe_process(state: GoodState) -> GoodState:
    try:
        result = risky_op(state["data"])
        return {"result": result, "status": "ok"}
    except Exception as e:
        return {"result": None, "status": "error", "error": str(e)}
```

### DON'T ❌
```python
# Vague state
class BadState(TypedDict):
    data: dict  # Too vague
    stuff: any  # No type

# Too many responsibilities
def do_everything(state: BadState) -> BadState:
    """100 lines of mixed logic"""
    pass

# No error handling
def unsafe(state: BadState) -> BadState:
    return {"result": risky_op(state["data"])}  # Can crash!
```

---

## 🚨 Common Errors & Solutions

### Error: KeyError
```python
# Problem: Field not in state
state["missing_field"]  # ❌

# Solution: Initialize all fields
class MyState(TypedDict):
    missing_field: str  # Define it!

initial = {"missing_field": ""}  # Initialize it!
```

### Error: Infinite Loop
```python
# Problem: No exit condition
def always_continue(state):
    return "continue"  # ❌ Never ends!

# Solution: Add limit
def smart_continue(state):
    if state["counter"] >= state["max"]:
        return "end"  # ✅ Exit condition
    return "continue"
```

### Error: Node Not Executing
```python
# Problem: Not connected
graph.add_node("orphan", func)  # ❌ No edges!

# Solution: Connect it
graph.add_node("connected", func)
graph.add_edge(START, "connected")  # ✅ Connected
graph.add_edge("connected", END)
```

### Error: State Not Updating
```python
# Problem: Not returning dict
def bad_node(state):
    state["field"] = "value"  # ❌ Doesn't work!

# Solution: Return dict
def good_node(state):
    return {"field": "value"}  # ✅ Works!
```

---

## 📚 Common Use Cases

### Use Case 1: Simple Chatbot
```python
class ChatState(TypedDict):
    messages: Annotated[list[dict], add]
    user_input: str
    response: str

def process_input(state):
    return {"messages": [{"role": "user", "content": state["user_input"]}]}

def generate_response(state):
    # Call LLM here
    response = llm.generate(state["messages"])
    return {
        "response": response,
        "messages": [{"role": "assistant", "content": response}]
    }
```

### Use Case 2: Data Pipeline
```python
class DataState(TypedDict):
    raw: str
    cleaned: str
    validated: bool
    result: dict

def load(state):
    return {"raw": fetch_data()}

def clean(state):
    return {"cleaned": state["raw"].strip()}

def validate(state):
    return {"validated": is_valid(state["cleaned"])}

def process(state):
    return {"result": transform(state["cleaned"])}
```

### Use Case 3: Multi-Step Analysis
```python
class AnalysisState(TypedDict):
    text: str
    word_count: int
    sentiment: str
    keywords: list[str]

# Parallel analysis
def count_words(state):
    return {"word_count": len(state["text"].split())}

def analyze_sentiment(state):
    return {"sentiment": get_sentiment(state["text"])}

def extract_keywords(state):
    return {"keywords": get_keywords(state["text"])}
```

---

## 🎯 Quick Commands

```python
# Create graph
graph = StateGraph(MyState)

# Add node
graph.add_node("name", function)

# Add normal edge
graph.add_edge("from", "to")

# Add conditional edge
graph.add_conditional_edges("source", router_func, {"path": "target"})

# Compile
workflow = graph.compile()

# Execute
result = workflow.invoke(initial_state)

# Stream (step by step)
for chunk in workflow.stream(initial_state):
    print(chunk)

# Visualize
print(workflow.get_graph())
```

---

## 💡 Tips & Tricks

1. **Start Simple**: Pehle linear workflow banayein, phir complexity add karen
2. **Test Nodes**: Har node ko independently test karen
3. **Use Print**: Debugging ke liye print statements add karen
4. **Handle Errors**: Har risky operation mein try-except use karen
5. **Document**: Docstrings aur comments add karen
6. **Visualize**: Graph structure ko visualize karen
7. **Parallel When Possible**: Independent tasks ko parallel run karen
8. **Avoid Deep Nesting**: Graph ko simple aur flat rakhen

---

## 🔗 Resources

- **Docs**: https://langchain-ai.github.io/langgraph/
- **Examples**: https://github.com/langchain-ai/langgraph/tree/main/examples
- **Discord**: LangChain Discord Community

---

**Happy Coding! 🚀**

*Quick Reference v1.0 - January 2026*

