# 🚀 LangGraph Foundation - Complete Guide

**Roman Urdu mein comprehensive guide for building stateful AI workflows**

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Installation & Setup](#installation--setup)
4. [Basic Examples](#basic-examples)
5. [Advanced Patterns](#advanced-patterns)
6. [Error Handling](#error-handling)
7. [Architecture](#architecture)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Real-World Projects](#real-world-projects)

---

## 🎯 Introduction

### LangGraph Kya Hai?

**LangGraph** ek powerful framework hai jo **stateful, multi-actor applications** banane ke liye design kiya gaya hai. Yeh LangChain ka extension hai jo specifically **cyclic workflows** aur **complex agent behaviors** handle karne ke liye bana hai.

### Key Features

- ✅ **Stateful Workflows**: State ko maintain karta hai across multiple steps
- ✅ **Cycles & Loops**: Iterative processes support karta hai
- ✅ **Parallel Processing**: Multiple operations simultaneously run kar sakta hai
- ✅ **Conditional Routing**: Dynamic decision making
- ✅ **Human-in-the-Loop**: Human intervention points add kar sakte hain
- ✅ **Error Handling**: Robust error recovery mechanisms

### Use Cases

1. **Chatbots with Memory**: Conversation history maintain karna
2. **Multi-Agent Systems**: Multiple AI agents coordination
3. **Data Processing Pipelines**: Complex ETL workflows
4. **Decision Trees**: Conditional logic based workflows
5. **Iterative Refinement**: Loop-based improvement processes

---

## 🧩 Core Concepts

### 1. State (حالت)

**State** graph ki current condition ko represent karta hai. Yeh ek shared data structure hai jo har node access kar sakta hai.

```python
from typing import TypedDict

class MyState(TypedDict):
    message: str
    count: int
    results: list[str]
```

**Key Points:**
- TypedDict ya Pydantic models use karen
- Saari fields clearly define karen
- Initial values provide karen

### 2. Nodes (نوڈز)

**Nodes** processing functions hain jo state ko read aur update karte hain.

```python
def my_node(state: MyState) -> MyState:
    """Process state and return updates"""
    return {
        "message": state["message"] + " processed",
        "count": state["count"] + 1
    }
```

**Key Points:**
- Input: current state
- Output: dictionary with state updates
- Sirf updated fields return karen (partial updates)

### 3. Edges (کنارے)

**Edges** nodes ke beech connections define karte hain.

**Types:**

a) **Normal Edges**: Direct connection
```python
graph.add_edge("node_a", "node_b")
```

b) **Conditional Edges**: Dynamic routing
```python
graph.add_conditional_edges(
    "node_a",
    routing_function,
    {
        "path1": "node_b",
        "path2": "node_c"
    }
)
```

### 4. Graph (گراف)

**Graph** complete workflow ko represent karta hai.

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(MyState)
graph.add_node("process", my_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)

workflow = graph.compile()
```

### 5. Reducers

**Reducers** state updates ko combine karne ka tareeqa define karte hain.

```python
from typing import Annotated
from operator import add

class StateWithReducer(TypedDict):
    messages: Annotated[list[str], add]  # Lists ko concatenate karega
```

**Common Reducers:**
- `operator.add`: Lists/numbers add karta hai
- Custom functions: Apna logic define karen

---

## 🛠️ Installation & Setup

### Prerequisites

```bash
# Python 3.9+ required
python --version
```

### Installation

```bash
# Virtual environment create karen
python -m venv venv

# Activate karen
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# LangGraph install karen
pip install langgraph

# Optional: LangChain aur OpenAI
pip install langchain langchain-openai openai
```

### Verification

```python
from langgraph.graph import StateGraph, START, END
print("✅ LangGraph successfully installed!")
```

---

## 📝 Basic Examples

### Example 1: Simple Linear Workflow

**Scenario**: Ek simple message processing workflow

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. State define karen
class SimpleState(TypedDict):
    message: str
    count: int

# 2. Nodes define karen
def add_greeting(state: SimpleState) -> SimpleState:
    return {
        "message": state["message"] + "Hello ",
        "count": state["count"] + 1
    }

def add_name(state: SimpleState) -> SimpleState:
    return {
        "message": state["message"] + "World!",
        "count": state["count"] + 1
    }

# 3. Graph banayein
graph = StateGraph(SimpleState)
graph.add_node("greeting", add_greeting)
graph.add_node("name", add_name)

# 4. Edges add karen
graph.add_edge(START, "greeting")
graph.add_edge("greeting", "name")
graph.add_edge("name", END)

# 5. Compile karen
workflow = graph.compile()

# 6. Execute karen
result = workflow.invoke({"message": "", "count": 0})
print(result)
# Output: {'message': 'Hello World!', 'count': 2}
```

**Flow Diagram:**
```
START → greeting → name → END
```

---

### Example 2: Parallel Processing

**Scenario**: Multiple calculations parallel mein run karen

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MathState(TypedDict):
    number: int
    squared: int
    cubed: int
    doubled: int

def square(state: MathState) -> MathState:
    return {"squared": state["number"] ** 2}

def cube(state: MathState) -> MathState:
    return {"cubed": state["number"] ** 3}

def double(state: MathState) -> MathState:
    return {"doubled": state["number"] * 2}

# Graph setup
graph = StateGraph(MathState)
graph.add_node("square", square)
graph.add_node("cube", cube)
graph.add_node("double", double)

# Parallel edges from START
graph.add_edge(START, "square")
graph.add_edge(START, "cube")
graph.add_edge(START, "double")

# All converge to END
graph.add_edge("square", END)
graph.add_edge("cube", END)
graph.add_edge("double", END)

workflow = graph.compile()
result = workflow.invoke({"number": 5})
print(result)
# Output: {'number': 5, 'squared': 25, 'cubed': 125, 'doubled': 10}
```

**Flow Diagram:**
```
        ┌→ square →┐
START →→┼→ cube   →┼→→ END
        └→ double →┘
```

---

### Example 3: Conditional Routing

**Scenario**: Input ke basis pe different paths choose karen

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class RouterState(TypedDict):
    age: int
    category: str
    message: str

def categorize(state: RouterState) -> RouterState:
    if state["age"] < 18:
        return {"category": "minor"}
    elif state["age"] < 65:
        return {"category": "adult"}
    else:
        return {"category": "senior"}

def handle_minor(state: RouterState) -> RouterState:
    return {"message": "Access restricted"}

def handle_adult(state: RouterState) -> RouterState:
    return {"message": "Full access granted"}

def handle_senior(state: RouterState) -> RouterState:
    return {"message": "Senior discount available"}

# Router function
def route_by_age(state: RouterState) -> Literal["minor", "adult", "senior"]:
    return state["category"]

# Graph setup
graph = StateGraph(RouterState)
graph.add_node("categorize", categorize)
graph.add_node("minor", handle_minor)
graph.add_node("adult", handle_adult)
graph.add_node("senior", handle_senior)

graph.add_edge(START, "categorize")
graph.add_conditional_edges(
    "categorize",
    route_by_age,
    {
        "minor": "minor",
        "adult": "adult",
        "senior": "senior"
    }
)

graph.add_edge("minor", END)
graph.add_edge("adult", END)
graph.add_edge("senior", END)

workflow = graph.compile()

# Test different ages
print(workflow.invoke({"age": 15}))
print(workflow.invoke({"age": 30}))
print(workflow.invoke({"age": 70}))
```

**Flow Diagram:**
```
                    ┌→ minor  → END
START → categorize →┼→ adult  → END
                    └→ senior → END
```

---

### Example 4: Loop/Cycle Workflow

**Scenario**: Iterative processing with loop

```python
from typing import TypedDict, Literal, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class LoopState(TypedDict):
    counter: int
    max_count: int
    history: Annotated[list[int], add]

def increment(state: LoopState) -> LoopState:
    new_count = state["counter"] + 1
    return {
        "counter": new_count,
        "history": [new_count]
    }

def should_continue(state: LoopState) -> Literal["continue", "end"]:
    if state["counter"] < state["max_count"]:
        return "continue"
    return "end"

# Graph setup
graph = StateGraph(LoopState)
graph.add_node("increment", increment)

graph.add_edge(START, "increment")
graph.add_conditional_edges(
    "increment",
    should_continue,
    {
        "continue": "increment",  # Loop back!
        "end": END
    }
)

workflow = graph.compile()
result = workflow.invoke({"counter": 0, "max_count": 5, "history": []})
print(result)
# Output: {'counter': 5, 'max_count': 5, 'history': [1, 2, 3, 4, 5]}
```

**Flow Diagram:**
```
START → increment ←┐
          ↓        │
       [check]     │
          ↓        │
    continue? ─────┘
          ↓
         END
```

---

## 🎨 Advanced Patterns

### Pattern 1: Fan-Out / Fan-In

**Use Case**: Parallel processing with aggregation

```python
from typing import TypedDict, Annotated
from operator import add

class FanState(TypedDict):
    input_data: str
    results: Annotated[list[str], add]

def process_a(state: FanState) -> FanState:
    return {"results": [f"A processed: {state['input_data']}"]}

def process_b(state: FanState) -> FanState:
    return {"results": [f"B processed: {state['input_data']}"]}

def process_c(state: FanState) -> FanState:
    return {"results": [f"C processed: {state['input_data']}"]}

def aggregate(state: FanState) -> FanState:
    combined = " | ".join(state["results"])
    return {"results": [f"Combined: {combined}"]}

# Graph
graph = StateGraph(FanState)
graph.add_node("a", process_a)
graph.add_node("b", process_b)
graph.add_node("c", process_c)
graph.add_node("aggregate", aggregate)

# Fan-out
graph.add_edge(START, "a")
graph.add_edge(START, "b")
graph.add_edge(START, "c")

# Fan-in
graph.add_edge("a", "aggregate")
graph.add_edge("b", "aggregate")
graph.add_edge("c", "aggregate")
graph.add_edge("aggregate", END)

workflow = graph.compile()
```

### Pattern 2: Retry Logic

**Use Case**: Error recovery with retries

```python
from typing import TypedDict, Literal

class RetryState(TypedDict):
    attempt: int
    max_attempts: int
    success: bool
    result: str

def try_operation(state: RetryState) -> RetryState:
    import random
    
    # Simulate random success/failure
    success = random.random() > 0.5
    
    return {
        "attempt": state["attempt"] + 1,
        "success": success,
        "result": "Success!" if success else "Failed"
    }

def should_retry(state: RetryState) -> Literal["retry", "success", "failed"]:
    if state["success"]:
        return "success"
    elif state["attempt"] < state["max_attempts"]:
        return "retry"
    else:
        return "failed"

# Graph with retry logic
graph = StateGraph(RetryState)
graph.add_node("try", try_operation)

graph.add_edge(START, "try")
graph.add_conditional_edges(
    "try",
    should_retry,
    {
        "retry": "try",      # Try again
        "success": END,      # Success!
        "failed": END        # Give up
    }
)

workflow = graph.compile()
```

### Pattern 3: Pipeline with Validation

**Use Case**: Data processing with validation steps

```python
class PipelineState(TypedDict):
    raw_data: str
    cleaned: str
    validated: bool
    processed: dict
    errors: Annotated[list[str], add]

def load(state: PipelineState) -> PipelineState:
    return {"raw_data": "  test@email.com, 25  "}

def clean(state: PipelineState) -> PipelineState:
    cleaned = state["raw_data"].strip()
    return {"cleaned": cleaned}

def validate(state: PipelineState) -> PipelineState:
    if "@" in state["cleaned"]:
        return {"validated": True}
    return {
        "validated": False,
        "errors": ["Invalid email format"]
    }

def process(state: PipelineState) -> PipelineState:
    email, age = state["cleaned"].split(",")
    return {
        "processed": {
            "email": email.strip(),
            "age": int(age.strip())
        }
    }

def handle_error(state: PipelineState) -> PipelineState:
    return {"processed": {}}

def route_validation(state: PipelineState) -> Literal["valid", "invalid"]:
    return "valid" if state["validated"] else "invalid"

# Pipeline graph
graph = StateGraph(PipelineState)
graph.add_node("load", load)
graph.add_node("clean", clean)
graph.add_node("validate", validate)
graph.add_node("process", process)
graph.add_node("error", handle_error)

graph.add_edge(START, "load")
graph.add_edge("load", "clean")
graph.add_edge("clean", "validate")
graph.add_conditional_edges(
    "validate",
    route_validation,
    {"valid": "process", "invalid": "error"}
)
graph.add_edge("process", END)
graph.add_edge("error", END)

workflow = graph.compile()
```

---

## 🛡️ Error Handling

### Strategy 1: Try-Catch in Nodes

```python
def safe_node(state: MyState) -> MyState:
    try:
        # Risky operation
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
            "error": f"ValueError: {str(e)}"
        }
    except Exception as e:
        return {
            "result": None,
            "status": "error",
            "error": f"Unexpected: {str(e)}"
        }
```

### Strategy 2: Error State Field

```python
class ErrorAwareState(TypedDict):
    data: str
    result: str
    errors: Annotated[list[str], add]
    status: str  # "ok", "error", "warning"

def process_with_errors(state: ErrorAwareState) -> ErrorAwareState:
    errors = []
    
    if not state["data"]:
        errors.append("Empty data")
        return {"status": "error", "errors": errors}
    
    try:
        result = process_data(state["data"])
        return {"result": result, "status": "ok"}
    except Exception as e:
        errors.append(str(e))
        return {"status": "error", "errors": errors}
```

### Strategy 3: Fallback Nodes

```python
def route_with_fallback(state: MyState) -> Literal["success", "error"]:
    return state["status"]

# Graph with fallback
graph.add_conditional_edges(
    "risky_operation",
    route_with_fallback,
    {
        "success": "continue_processing",
        "error": "fallback_handler"
    }
)
```

### Strategy 4: Validation Layer

```python
def validate_input(state: MyState) -> MyState:
    """Validate before processing"""
    errors = []
    
    # Check required fields
    if not state.get("required_field"):
        errors.append("Missing required field")
    
    # Check data types
    if not isinstance(state.get("number"), int):
        errors.append("Number must be integer")
    
    # Check ranges
    if state.get("age", 0) < 0:
        errors.append("Age cannot be negative")
    
    return {
        "validated": len(errors) == 0,
        "errors": errors
    }
```

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
│  (Your business logic, API endpoints, UI)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  LANGGRAPH LAYER                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  StateGraph (Workflow Definition)                │  │
│  │  ├─ Nodes (Processing Units)                     │  │
│  │  ├─ Edges (Flow Control)                         │  │
│  │  └─ State (Shared Data)                          │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  EXECUTION LAYER                        │
│  ├─ State Management                                   │
│  ├─ Node Execution                                     │
│  ├─ Edge Traversal                                     │
│  └─ Result Collection                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              INTEGRATION LAYER                          │
│  ├─ LLM APIs (OpenAI, Anthropic, etc.)                │
│  ├─ Databases                                          │
│  ├─ External Services                                  │
│  └─ Vector Stores                                      │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User Input
    ↓
[StateGraph.invoke()]
    ↓
Initial State Created
    ↓
START Node
    ↓
┌─────────────────┐
│  Node Execution │ ←─┐
│  ├─ Read State  │   │
│  ├─ Process     │   │
│  └─ Update State│   │
└────────┬────────┘   │
         ↓            │
   Edge Traversal     │
         ↓            │
   Next Node?  ───────┘
         ↓
        END
         ↓
   Final State
         ↓
    User Output
```

### State Management Flow

```
┌──────────────────────────────────────────────────────┐
│              STATE LIFECYCLE                         │
└──────────────────────────────────────────────────────┘

1. INITIALIZATION
   Initial State → Type Validation → Default Values

2. NODE PROCESSING
   Current State → Node Function → Partial Update

3. STATE MERGING
   Old State + Update → Reducer Application → New State

4. PROPAGATION
   New State → Next Node(s) → Continue...

5. FINALIZATION
   Last Node → END → Final State → Return
```

---

## ✅ Best Practices

### 1. State Design

**DO:**
```python
# ✅ Clear, typed state
class GoodState(TypedDict):
    user_id: str
    messages: Annotated[list[str], add]
    count: int
    metadata: dict
```

**DON'T:**
```python
# ❌ Unclear, untyped state
class BadState(TypedDict):
    data: dict  # Too vague
    stuff: any  # No type info
    x: int      # Unclear name
```

### 2. Node Design

**DO:**
```python
# ✅ Focused, single responsibility
def validate_email(state: MyState) -> MyState:
    """Validate email format only"""
    is_valid = "@" in state["email"]
    return {"email_valid": is_valid}

def validate_age(state: MyState) -> MyState:
    """Validate age range only"""
    is_valid = 0 < state["age"] < 150
    return {"age_valid": is_valid}
```

**DON'T:**
```python
# ❌ Too many responsibilities
def validate_everything(state: MyState) -> MyState:
    """Does too much"""
    # Validates email, age, phone, address, etc.
    # 100+ lines of code
    pass
```

### 3. Error Handling

**DO:**
```python
# ✅ Graceful error handling
def safe_process(state: MyState) -> MyState:
    try:
        result = risky_operation(state["data"])
        return {"result": result, "status": "ok"}
    except SpecificError as e:
        logger.error(f"Error: {e}")
        return {
            "result": None,
            "status": "error",
            "error_message": str(e)
        }
```

**DON'T:**
```python
# ❌ Unhandled errors
def unsafe_process(state: MyState) -> MyState:
    result = risky_operation(state["data"])  # Might crash!
    return {"result": result}
```

### 4. Graph Structure

**DO:**
```python
# ✅ Clear, logical flow
graph.add_edge(START, "validate")
graph.add_edge("validate", "process")
graph.add_edge("process", "save")
graph.add_edge("save", END)
```

**DON'T:**
```python
# ❌ Confusing, spaghetti flow
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", "a")  # Unnecessary cycle
graph.add_edge("a", "c")
graph.add_edge("c", "b")  # Confusing
```

### 5. Testing

**DO:**
```python
# ✅ Test nodes independently
def test_validate_email():
    state = {"email": "test@example.com"}
    result = validate_email(state)
    assert result["email_valid"] == True

# ✅ Test graph paths
def test_happy_path():
    result = workflow.invoke(valid_input)
    assert result["status"] == "success"

def test_error_path():
    result = workflow.invoke(invalid_input)
    assert result["status"] == "error"
```

### 6. Performance

**DO:**
```python
# ✅ Use parallel edges for independent operations
graph.add_edge(START, "task1")
graph.add_edge(START, "task2")  # Runs parallel
graph.add_edge(START, "task3")  # Runs parallel
```

**DON'T:**
```python
# ❌ Unnecessary sequential execution
graph.add_edge(START, "task1")
graph.add_edge("task1", "task2")  # Could be parallel
graph.add_edge("task2", "task3")  # Could be parallel
```

### 7. Documentation

**DO:**
```python
# ✅ Well documented
def process_user_data(state: UserState) -> UserState:
    """
    Process and validate user data.
    
    Args:
        state: Current state with user_data field
        
    Returns:
        Updated state with processed_data and validation_status
        
    Raises:
        No exceptions (handles internally)
    """
    pass
```

---

## 🔧 Troubleshooting

### Problem 1: KeyError in State

**Error:**
```python
KeyError: 'field_name'
```

**Solution:**
```python
# ✅ Initialize all fields
class MyState(TypedDict):
    field_name: str  # Define it!

# ✅ Provide initial values
initial_state = {
    "field_name": ""  # Initialize it!
}
```

### Problem 2: Infinite Loop

**Error:**
Graph keeps running forever

**Solution:**
```python
# ✅ Add exit condition
class LoopState(TypedDict):
    counter: int
    max_iterations: int  # Add limit!

def should_continue(state: LoopState) -> Literal["continue", "end"]:
    if state["counter"] >= state["max_iterations"]:
        return "end"  # Exit condition!
    return "continue"
```

### Problem 3: Node Not Executing

**Symptoms:**
Node function not being called

**Solutions:**
```python
# ✅ Check node is added
graph.add_node("my_node", my_function)

# ✅ Check edges connect to it
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)

# ✅ Check conditional routing
def router(state):
    return "my_node"  # Must return correct node name
```

### Problem 4: State Not Updating

**Symptoms:**
Node runs but state doesn't change

**Solutions:**
```python
# ✅ Return dictionary
def my_node(state: MyState) -> MyState:
    return {"field": "new_value"}  # Must return dict!

# ✅ Use correct field names
return {"field_name": value}  # Match TypedDict exactly

# ✅ Use reducer for lists
class MyState(TypedDict):
    items: Annotated[list, add]  # Need reducer!
```

### Problem 5: Type Errors

**Error:**
```python
TypeError: ... is not a valid TypedDict
```

**Solution:**
```python
# ✅ Match types exactly
class MyState(TypedDict):
    count: int  # Not str!
    
def my_node(state: MyState) -> MyState:
    return {"count": 42}  # int, not "42"
```

### Problem 6: Compilation Fails

**Error:**
```python
ValueError: Graph is not valid
```

**Solutions:**
```python
# ✅ Check START is connected
graph.add_edge(START, "first_node")

# ✅ Check END is reachable
graph.add_edge("last_node", END)

# ✅ Check all conditional paths
graph.add_conditional_edges(
    "router",
    route_func,
    {
        "path1": "node1",  # All paths must exist
        "path2": "node2"
    }
)
```

---

## 🚀 Real-World Projects

### Project 1: Simple Chatbot

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class ChatState(TypedDict):
    messages: Annotated[list[dict], add]
    user_input: str
    bot_response: str

def process_input(state: ChatState) -> ChatState:
    """Process user input"""
    user_msg = {
        "role": "user",
        "content": state["user_input"]
    }
    return {"messages": [user_msg]}

def generate_response(state: ChatState) -> ChatState:
    """Generate bot response (placeholder for LLM)"""
    # In real app, call OpenAI/Anthropic here
    response = f"You said: {state['user_input']}"
    
    bot_msg = {
        "role": "assistant",
        "content": response
    }
    
    return {
        "bot_response": response,
        "messages": [bot_msg]
    }

# Build chatbot
graph = StateGraph(ChatState)
graph.add_node("process", process_input)
graph.add_node("generate", generate_response)

graph.add_edge(START, "process")
graph.add_edge("process", "generate")
graph.add_edge("generate", END)

chatbot = graph.compile()

# Use it
result = chatbot.invoke({
    "messages": [],
    "user_input": "Hello!"
})
print(result["bot_response"])
```

### Project 2: Data Validation Pipeline

```python
class DataState(TypedDict):
    raw_data: dict
    validated_data: dict
    errors: Annotated[list[str], add]
    status: str

def validate_schema(state: DataState) -> DataState:
    """Validate data schema"""
    required_fields = ["name", "email", "age"]
    errors = []
    
    for field in required_fields:
        if field not in state["raw_data"]:
            errors.append(f"Missing field: {field}")
    
    return {
        "status": "schema_valid" if not errors else "schema_invalid",
        "errors": errors
    }

def validate_values(state: DataState) -> DataState:
    """Validate field values"""
    errors = []
    data = state["raw_data"]
    
    if "@" not in data.get("email", ""):
        errors.append("Invalid email format")
    
    if not (0 < data.get("age", -1) < 150):
        errors.append("Invalid age range")
    
    return {
        "status": "values_valid" if not errors else "values_invalid",
        "errors": errors
    }

def save_data(state: DataState) -> DataState:
    """Save validated data"""
    # Save to database here
    return {
        "validated_data": state["raw_data"],
        "status": "saved"
    }

def handle_invalid(state: DataState) -> DataState:
    """Handle invalid data"""
    return {"status": "rejected"}

def route_validation(state: DataState) -> Literal["valid", "invalid"]:
    return "valid" if "valid" in state["status"] else "invalid"

# Build pipeline
graph = StateGraph(DataState)
graph.add_node("schema", validate_schema)
graph.add_node("values", validate_values)
graph.add_node("save", save_data)
graph.add_node("reject", handle_invalid)

graph.add_edge(START, "schema")
graph.add_conditional_edges(
    "schema",
    route_validation,
    {"valid": "values", "invalid": "reject"}
)
graph.add_conditional_edges(
    "values",
    route_validation,
    {"valid": "save", "invalid": "reject"}
)
graph.add_edge("save", END)
graph.add_edge("reject", END)

pipeline = graph.compile()
```

### Project 3: Multi-Step Analysis

```python
class AnalysisState(TypedDict):
    text: str
    word_count: int
    sentiment: str
    keywords: list[str]
    summary: str

def count_words(state: AnalysisState) -> AnalysisState:
    """Count words in text"""
    count = len(state["text"].split())
    return {"word_count": count}

def analyze_sentiment(state: AnalysisState) -> AnalysisState:
    """Analyze sentiment (placeholder)"""
    # Use actual sentiment analysis library
    sentiment = "positive"  # Simplified
    return {"sentiment": sentiment}

def extract_keywords(state: AnalysisState) -> AnalysisState:
    """Extract keywords (placeholder)"""
    # Use actual keyword extraction
    words = state["text"].split()
    keywords = words[:5]  # Simplified
    return {"keywords": keywords}

def create_summary(state: AnalysisState) -> AnalysisState:
    """Create summary"""
    summary = f"Text has {state['word_count']} words, "
    summary += f"sentiment is {state['sentiment']}, "
    summary += f"keywords: {', '.join(state['keywords'])}"
    return {"summary": summary}

# Build analyzer
graph = StateGraph(AnalysisState)
graph.add_node("words", count_words)
graph.add_node("sentiment", analyze_sentiment)
graph.add_node("keywords", extract_keywords)
graph.add_node("summary", create_summary)

# Parallel analysis
graph.add_edge(START, "words")
graph.add_edge(START, "sentiment")
graph.add_edge(START, "keywords")

# Converge to summary
graph.add_edge("words", "summary")
graph.add_edge("sentiment", "summary")
graph.add_edge("keywords", "summary")
graph.add_edge("summary", END)

analyzer = graph.compile()
```

---

## 📚 Additional Resources

### Official Documentation
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Docs**: https://python.langchain.com/
- **GitHub Repo**: https://github.com/langchain-ai/langgraph

### Tutorials & Examples
- LangGraph Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
- LangChain Blog: https://blog.langchain.dev/
- YouTube Tutorials: Search "LangGraph tutorial"

### Community
- Discord: LangChain Discord Server
- GitHub Discussions: https://github.com/langchain-ai/langgraph/discussions
- Twitter: @LangChainAI

### Related Technologies
- **LangChain**: Base framework for LLM applications
- **LangSmith**: Monitoring and debugging tool
- **LangServe**: Deployment framework

---

## 🎓 Summary

### Key Takeaways

1. **LangGraph** stateful workflows ke liye perfect hai
2. **State, Nodes, Edges** - teen core components
3. **Parallel processing** performance improve karta hai
4. **Conditional routing** dynamic workflows enable karta hai
5. **Error handling** production apps ke liye essential hai
6. **Reducers** state accumulation ke liye use karen
7. **Start simple**, gradually complexity add karen

### Next Steps

1. ✅ Basic examples run karen
2. ✅ Apna pehla simple workflow banayein
3. ✅ Error handling add karen
4. ✅ LLM integration try karen
5. ✅ Real project start karen

### Common Patterns Recap

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| Linear | Simple pipelines | ⭐ Easy |
| Parallel | Independent tasks | ⭐⭐ Medium |
| Conditional | Dynamic routing | ⭐⭐ Medium |
| Loop | Iterative processing | ⭐⭐⭐ Advanced |
| Fan-out/Fan-in | Parallel + Aggregate | ⭐⭐⭐ Advanced |

---

## 📝 Quick Reference

### Essential Imports
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from operator import add
```

### Basic Template
```python
# 1. Define State
class MyState(TypedDict):
    field: str

# 2. Define Nodes
def my_node(state: MyState) -> MyState:
    return {"field": "value"}

# 3. Build Graph
graph = StateGraph(MyState)
graph.add_node("node", my_node)
graph.add_edge(START, "node")
graph.add_edge("node", END)

# 4. Compile & Run
workflow = graph.compile()
result = workflow.invoke({"field": ""})
```

### Common Operations

**Add Node:**
```python
graph.add_node("name", function)
```

**Add Edge:**
```python
graph.add_edge("from", "to")
```

**Add Conditional Edge:**
```python
graph.add_conditional_edges(
    "source",
    router_function,
    {"option1": "target1", "option2": "target2"}
)
```

**Compile:**
```python
workflow = graph.compile()
```

**Execute:**
```python
result = workflow.invoke(initial_state)
```

---

## ✨ Conclusion

LangGraph ek powerful tool hai complex AI workflows banane ke liye. Yeh guide aapko foundation se lekar advanced patterns tak sab kuch sikhata hai.

**Remember:**
- Start simple
- Test thoroughly
- Handle errors gracefully
- Document your code
- Keep learning!

**Happy Coding! 🚀**

---

*Guide created: January 2026*  
*Version: 1.0*  
*Language: Roman Urdu*

