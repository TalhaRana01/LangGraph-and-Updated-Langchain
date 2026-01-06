# LangGraph Conditional Workflow Guide

## Table of Contents
1. [Concept](#concept)
2. [Kab Use Karein](#kab-use-karein)
3. [Core Components](#core-components)
4. [Method 1: Direct Routing](#method-1-direct-routing)
5. [Method 2: Router Node (Explicit)](#method-2-router-node-explicit)
6. [Best Practices](#best-practices)
7. [Common Use-Cases](#common-use-cases)

---

## Concept

**Conditional Workflow** ka matlab hai ke graph execution ke dauran **run-time pe decision** hota hai ke next node konsa chalega—yani if/else type routing.

### Key Points:
- **State-based routing**: Decision `state` ke kisi field (e.g. `intent`, `score`, `flag`) ki basis pe hota hai.
- **Multiple possible paths**: Ek node ke baad different branches mein ja sakte ho (A→B ya A→C).
- **Converge bhi ho sakta**: Different branches baad mein same final node pe aa sakti hain.

### Visual Structure:
```
START → Node A → (decision) → Node B (if condition true)
                           → Node C (if condition false)
                           → END
```

---

## Kab Use Karein

Conditional workflows tab use karein jab:
- **Intent detection** karna ho (user query ke basis pe different handlers)
- **Quality checks** ho (pass/fail, approve/reject)
- **Threshold-based routing** (score >= 50 → pass, else fail)
- **Tool selection** (dynamic tool calling based on query type)
- **Retry/repair loops** (agar output galat ho to revise node chalao)
- **Moderation** (content safe hai to proceed, else block)

---

## Core Components

### 1. Router/Decider Function
Ek function jo state dekh kar **route key** (string) return karta hai:
```python
def route_by_score(state: SimpleState) -> str:
    return "pass" if state.get("score", 0) >= 50 else "fail"
```

### 2. `add_conditional_edges`
LangGraph ka method jo ek node se multiple possible next nodes ka mapping karta hai:
```python
graph.add_conditional_edges(
    "source_node",        # Source node (ya START)
    router_function,      # Function jo route key return kare
    {                     # Mapping: route key → target node
        "pass": "pass_node",
        "fail": "fail_node"
    }
)
```

### 3. Fallback/Default Route
Agar router unexpected value return kare to default path hona chahiye:
```python
def router_with_fallback(state):
    score = state.get("score", 0)
    if score >= 80:
        return "excellent"
    elif score >= 50:
        return "pass"
    else:
        return "fail"
```

---

## Method 1: Direct Routing

Is method mein router function **directly START se** conditional routing karta hai.

### Code Example:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class SimpleState(TypedDict, total=False):
    name: str
    score: int
    result: str
    message: str


def route_by_score(state: SimpleState) -> str:
    """Router function: state dekh kar route decide karta hai"""
    return "pass" if state.get("score", 0) >= 50 else "fail"


def pass_node(state: SimpleState) -> SimpleState:
    return {
        "result": "PASS",
        "message": f"{state.get('name', 'Student')} passed with score {state.get('score', 0)}.",
    }


def fail_node(state: SimpleState) -> SimpleState:
    return {
        "result": "FAIL",
        "message": f"{state.get('name', 'Student')} failed with score {state.get('score', 0)}.",
    }


# Graph banao
graph = StateGraph(SimpleState)

graph.add_node("pass", pass_node)
graph.add_node("fail", fail_node)

# START se conditional routing
graph.add_conditional_edges(START, route_by_score, {"pass": "pass", "fail": "fail"})

graph.add_edge("pass", END)
graph.add_edge("fail", END)

workflow = graph.compile()

# Run examples
print(workflow.invoke({"name": "Ali", "score": 78}))
# Output: {'name': 'Ali', 'score': 78, 'result': 'PASS', 'message': 'Ali passed with score 78.'}

print(workflow.invoke({"name": "Sara", "score": 35}))
# Output: {'name': 'Sara', 'score': 35, 'result': 'FAIL', 'message': 'Sara failed with score 35.'}
```

### Pros:
- Simple aur concise
- Jaldi prototyping ke liye best

### Cons:
- Decision state mein store nahi hota (debugging mushkil)
- Router logic zyada complex hone par maintain karna hard

---

## Method 2: Router Node (Explicit)

Is method mein pehle ek **router node** chalta hai jo decision ko **state mein store** karta hai, phir conditional edges us node se aage route karti hain.

### Code Example:

```python
from typing import Literal


class RoutedState(SimpleState, total=False):
    route: Literal["pass", "fail"]


def router_node(state: RoutedState) -> RoutedState:
    """Router node: decision ko state mein store karta hai"""
    route = "pass" if state.get("score", 0) >= 50 else "fail"
    return {"route": route}


def read_route(state: RoutedState) -> str:
    """Conditional function: state se route read karta hai"""
    return state.get("route", "fail")


# Graph banao
graph2 = StateGraph(RoutedState)

graph2.add_node("router", router_node)
graph2.add_node("pass", pass_node)
graph2.add_node("fail", fail_node)

graph2.add_edge(START, "router")

# Router node se conditional routing
graph2.add_conditional_edges(
    "router",
    read_route,
    {"pass": "pass", "fail": "fail"},
)

graph2.add_edge("pass", END)
graph2.add_edge("fail", END)

workflow2 = graph2.compile()

# Run examples
print(workflow2.invoke({"name": "Hassan", "score": 51}))
# Output: {'name': 'Hassan', 'score': 51, 'route': 'pass', 'result': 'PASS', 'message': 'Hassan passed with score 51.'}

print(workflow2.invoke({"name": "Ayesha", "score": 12}))
# Output: {'name': 'Ayesha', 'score': 12, 'route': 'fail', 'result': 'FAIL', 'message': 'Ayesha failed with score 12.'}
```

### Pros:
- Decision (`route`) state mein save hota hai → **debugging/logging easy**
- Complex rules (multiple flags/thresholds) maintain karna simple
- Routing logic ko test karna alag se possible

### Cons:
- Thora zyada verbose code

---

## Best Practices

### 1. **Fallback/Default Route** Hamesha Rakhein
```python
def safe_router(state):
    route = state.get("route")
    if route in ["pass", "fail"]:
        return route
    return "default"  # fallback

graph.add_conditional_edges(
    "router",
    safe_router,
    {"pass": "pass", "fail": "fail", "default": "error_handler"}
)
```

### 2. **Type Hints Use Karein**
`Literal` types se IDE autocomplete aur type checking improve hoti hai:
```python
from typing import Literal

def router(state) -> Literal["pass", "fail"]:
    return "pass" if state["score"] >= 50 else "fail"
```

### 3. **Decision Ko Log/Store Karein**
Debugging ke liye decision state mein save karna best hai (Method 2 prefer karein).

### 4. **Router Logic Ko Test Karein**
Router function ko alag se unit test karein:
```python
def test_router():
    assert route_by_score({"score": 60}) == "pass"
    assert route_by_score({"score": 30}) == "fail"
```

### 5. **Complex Routing Ko Modular Banayein**
Agar bahut saari conditions hain to helper functions banayein:
```python
def is_high_quality(state):
    return state.get("score", 0) >= 80

def is_passing(state):
    return state.get("score", 0) >= 50

def router(state):
    if is_high_quality(state):
        return "excellent"
    elif is_passing(state):
        return "pass"
    else:
        return "fail"
```

### 6. **Missing Keys Handle Karein**
`state.get()` ya try-except use karein:
```python
def safe_router(state):
    score = state.get("score")
    if score is None:
        return "error"
    return "pass" if score >= 50 else "fail"
```

---

## Common Use-Cases

### Use-Case 1: Intent Detection (Chatbot)
```python
def detect_intent(state):
    query = state.get("query", "").lower()
    if "weather" in query:
        return "weather_handler"
    elif "news" in query:
        return "news_handler"
    else:
        return "general_handler"

graph.add_conditional_edges(
    START,
    detect_intent,
    {
        "weather_handler": "weather_node",
        "news_handler": "news_node",
        "general_handler": "general_node"
    }
)
```

### Use-Case 2: Quality Check (Content Moderation)
```python
def moderate_content(state):
    is_safe = check_safety(state.get("text"))
    return "approve" if is_safe else "reject"

graph.add_conditional_edges(
    "moderation_node",
    moderate_content,
    {"approve": "publish_node", "reject": "block_node"}
)
```

### Use-Case 3: Retry Loop (Error Handling)
```python
def check_quality(state):
    if state.get("attempts", 0) >= 3:
        return "give_up"
    if is_valid_output(state.get("output")):
        return "success"
    return "retry"

graph.add_conditional_edges(
    "validator",
    check_quality,
    {
        "success": END,
        "retry": "regenerate_node",
        "give_up": "error_node"
    }
)
```

### Use-Case 4: Multi-Threshold Scoring
```python
def grade_router(state):
    score = state.get("score", 0)
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

graph.add_conditional_edges(
    START,
    grade_router,
    {
        "A": "grade_A_node",
        "B": "grade_B_node",
        "C": "grade_C_node",
        "D": "grade_D_node",
        "F": "grade_F_node"
    }
)
```

---

## Summary

| Feature | Method 1 (Direct) | Method 2 (Router Node) |
|---------|------------------|------------------------|
| Simplicity | ✅ Simple | ⚠️ Thora verbose |
| Decision Logging | ❌ Nahi | ✅ State mein save |
| Debugging | ⚠️ Mushkil | ✅ Easy |
| Complex Rules | ⚠️ Hard to maintain | ✅ Easy to maintain |
| Best For | Quick prototypes | Production code |

**Recommendation**: Production mein **Method 2** prefer karein (router node explicit), quick prototyping mein **Method 1** use kar sakte hain.

---

## Quick Reference

### Basic Pattern:
```python
# Router function
def router(state) -> str:
    return "route_key_based_on_state"

# Add conditional edges
graph.add_conditional_edges(
    "source_node",
    router,
    {
        "route_A": "node_A",
        "route_B": "node_B"
    }
)
```

### With Explicit Router Node:
```python
# Router node (decision ko state mein store)
def router_node(state):
    route = compute_route(state)
    return {"route": route}

# Reader function
def read_route(state) -> str:
    return state["route"]

# Add edges
graph.add_edge(START, "router")
graph.add_conditional_edges("router", read_route, mapping)
```

---

**Happy Coding! 🚀**

