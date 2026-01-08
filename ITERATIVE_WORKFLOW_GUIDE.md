# 🔄 LangGraph Iterative Workflow - Complete Guide

**Roman Urdu mein comprehensive guide for building iterative and cyclic workflows**

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Kab Use Karein](#kab-use-karein)
4. [Basic Patterns](#basic-patterns)
5. [Advanced Examples](#advanced-examples)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Troubleshooting](#troubleshooting)
10. [Complete Projects](#complete-projects)

---

## 🎯 Introduction

### Iterative Workflow Kya Hai?

**Iterative Workflow** ek aisa pattern hai jahan graph execution **loop mein chalta hai** - yani ek node apne aap ko ya previous nodes ko **repeatedly call** karta hai jab tak koi condition satisfy na ho jaye.

### Key Characteristics

- ✅ **Loops/Cycles**: Nodes ek doosre ko repeatedly call karte hain
- ✅ **Progressive Improvement**: Har iteration mein output better hota hai
- ✅ **Conditional Exit**: Loop tab rukta hai jab condition meet ho jaye
- ✅ **State Accumulation**: Har iteration state ko update karta hai
- ✅ **Bounded Execution**: Infinite loops se bachne ke liye limits hoti hain

### Visual Structure

```
START → Process → Check Quality
           ↑            ↓
           └─── Retry ──┘ (if not good enough)
                ↓
               END (if good enough)
```

### Difference: Conditional vs Iterative

| Feature | Conditional Workflow | Iterative Workflow |
|---------|---------------------|-------------------|
| **Flow** | Linear branches | Cyclic loops |
| **Repetition** | Ek baar decision | Multiple iterations |
| **Use Case** | Route selection | Progressive refinement |
| **Exit** | Immediate | Condition-based |

---

## 🧩 Core Concepts

### 1. Loop Counter

Har iteration ko track karne ke liye counter use karte hain:

```python
class IterativeState(TypedDict):
    counter: int        # Current iteration number
    max_iterations: int # Maximum allowed iterations
```

**Purpose:**
- Infinite loops se bachna
- Progress tracking
- Debugging help

### 2. Exit Condition

Loop kab rukna hai yeh decide karta hai:

```python
def should_continue(state: IterativeState) -> Literal["continue", "end"]:
    # Check if max iterations reached
    if state["counter"] >= state["max_iterations"]:
        return "end"
    
    # Check if quality threshold met
    if state["quality_score"] >= 0.8:
        return "end"
    
    # Otherwise continue
    return "continue"
```

**Common Exit Conditions:**
- Maximum iterations reached
- Quality threshold achieved
- Error count exceeded
- Time limit reached
- User intervention

### 3. State Accumulation

Har iteration mein state ko update karna:

```python
from typing import Annotated
from operator import add

class AccumulativeState(TypedDict):
    attempts: int
    results: Annotated[list[str], add]  # Accumulates across iterations
    current_result: str                  # Overwritten each iteration
```

**Two Types:**
- **Accumulative**: Lists/arrays jo grow hote hain (use `Annotated[list, add]`)
- **Overwrite**: Values jo replace hoti hain (normal fields)

### 4. Feedback Loop

Previous iteration ka output next iteration ka input banta hai:

```python
def refine(state: RefineState) -> RefineState:
    previous_output = state["output"]
    feedback = state["feedback"]
    
    # Use previous output + feedback to improve
    improved_output = improve(previous_output, feedback)
    
    return {
        "output": improved_output,
        "iteration": state["iteration"] + 1
    }
```

---

## 📍 Kab Use Karein

### Perfect Use Cases

1. **Content Refinement**
   - Blog post ko iteratively improve karna
   - Code ko repeatedly fix karna
   - Design ko progressively enhance karna

2. **Quality Improvement**
   - Output ko quality threshold tak improve karna
   - Errors ko iteratively fix karna
   - Validation failures ko resolve karna

3. **Search & Optimization**
   - Best solution dhoondhna through multiple attempts
   - Parameters ko tune karna
   - A/B testing iterations

4. **Retry Logic**
   - Failed operations ko retry karna
   - Network requests with exponential backoff
   - Database transactions with retries

5. **Progressive Generation**
   - Step-by-step content generation
   - Incremental data processing
   - Multi-stage calculations

6. **Self-Correction**
   - LLM outputs ko self-evaluate aur improve karna
   - Automated debugging
   - Error recovery loops

### Avoid Kab Karein

❌ **Simple one-time operations** - Use linear workflow
❌ **Independent parallel tasks** - Use parallel workflow
❌ **Simple branching** - Use conditional workflow
❌ **Deterministic single-pass** - Use linear workflow

---

## 🔨 Basic Patterns

### Pattern 1: Simple Counter Loop

**Scenario**: Ek simple counter jo specified limit tak count karta hai

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from operator import add

class CounterState(TypedDict):
    counter: int
    max_count: int
    history: Annotated[list[int], add]

def increment(state: CounterState) -> CounterState:
    """Increment counter and record in history"""
    new_count = state["counter"] + 1
    print(f"Iteration {new_count}")
    return {
        "counter": new_count,
        "history": [new_count]
    }

def should_continue(state: CounterState) -> Literal["continue", "end"]:
    """Check if we should continue looping"""
    if state["counter"] >= state["max_count"]:
        return "end"
    return "continue"

# Build graph
graph = StateGraph(CounterState)
graph.add_node("increment", increment)

graph.add_edge(START, "increment")
graph.add_conditional_edges(
    "increment",
    should_continue,
    {
        "continue": "increment",  # Loop back to itself!
        "end": END
    }
)

workflow = graph.compile()

# Run
result = workflow.invoke({
    "counter": 0,
    "max_count": 5,
    "history": []
})

print(result)
# Output: {'counter': 5, 'max_count': 5, 'history': [1, 2, 3, 4, 5]}
```

**Flow Diagram:**
```
START → increment ←─┐
           ↓        │
      [check count] │
           ↓        │
    counter < max? ─┘
           ↓
          END
```

---

### Pattern 2: Quality-Based Iteration

**Scenario**: Output ko improve karte raho jab tak quality threshold achieve na ho

```python
class QualityState(TypedDict):
    text: str
    quality_score: float
    iteration: int
    max_iterations: int
    improvements: Annotated[list[str], add]

def generate_text(state: QualityState) -> QualityState:
    """Generate or improve text"""
    if state["iteration"] == 0:
        # First generation
        text = "This is initial text."
    else:
        # Improve existing text
        text = state["text"] + " Improved version."
    
    return {
        "text": text,
        "iteration": state["iteration"] + 1,
        "improvements": [f"Iteration {state['iteration'] + 1} completed"]
    }

def evaluate_quality(state: QualityState) -> QualityState:
    """Evaluate text quality"""
    # Simulate quality scoring (in real app, use actual metrics)
    quality = min(0.5 + (state["iteration"] * 0.15), 1.0)
    
    return {"quality_score": quality}

def check_quality(state: QualityState) -> Literal["improve", "done"]:
    """Decide if we need more iterations"""
    # Exit if max iterations reached
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    
    # Exit if quality is good enough
    if state["quality_score"] >= 0.8:
        return "done"
    
    # Otherwise, improve more
    return "improve"

# Build graph
graph = StateGraph(QualityState)
graph.add_node("generate", generate_text)
graph.add_node("evaluate", evaluate_quality)

graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    check_quality,
    {
        "improve": "generate",  # Loop back!
        "done": END
    }
)

workflow = graph.compile()

# Run
result = workflow.invoke({
    "text": "",
    "quality_score": 0.0,
    "iteration": 0,
    "max_iterations": 10,
    "improvements": []
})

print(f"Final quality: {result['quality_score']}")
print(f"Total iterations: {result['iteration']}")
print(f"Final text: {result['text']}")
```

**Flow Diagram:**
```
START → generate → evaluate ←─┐
                      ↓        │
                 [check]       │
                      ↓        │
         quality < 0.8? ───────┘
                      ↓
                    END
```

---

### Pattern 3: Retry with Exponential Backoff

**Scenario**: Failed operations ko retry karna with increasing delays

```python
import time
from typing import TypedDict, Literal, Annotated
from operator import add

class RetryState(TypedDict):
    attempt: int
    max_attempts: int
    success: bool
    result: str
    errors: Annotated[list[str], add]
    backoff_seconds: float

def try_operation(state: RetryState) -> RetryState:
    """Attempt the operation"""
    import random
    
    attempt_num = state["attempt"] + 1
    print(f"Attempt {attempt_num}...")
    
    # Simulate operation (70% failure rate for demo)
    success = random.random() > 0.7
    
    if success:
        return {
            "attempt": attempt_num,
            "success": True,
            "result": "Operation succeeded!",
            "backoff_seconds": 0
        }
    else:
        # Calculate exponential backoff: 2^attempt seconds
        backoff = 2 ** attempt_num
        
        return {
            "attempt": attempt_num,
            "success": False,
            "result": "",
            "errors": [f"Attempt {attempt_num} failed"],
            "backoff_seconds": backoff
        }

def wait_backoff(state: RetryState) -> RetryState:
    """Wait before retrying"""
    if state["backoff_seconds"] > 0:
        print(f"Waiting {state['backoff_seconds']} seconds before retry...")
        time.sleep(min(state["backoff_seconds"], 5))  # Cap at 5 seconds for demo
    return {}

def should_retry(state: RetryState) -> Literal["retry", "success", "failed"]:
    """Decide whether to retry"""
    if state["success"]:
        return "success"
    elif state["attempt"] >= state["max_attempts"]:
        return "failed"
    else:
        return "retry"

# Build graph
graph = StateGraph(RetryState)
graph.add_node("try", try_operation)
graph.add_node("wait", wait_backoff)

graph.add_edge(START, "try")
graph.add_conditional_edges(
    "try",
    should_retry,
    {
        "retry": "wait",
        "success": END,
        "failed": END
    }
)
graph.add_edge("wait", "try")  # After waiting, try again

workflow = graph.compile()

# Run
result = workflow.invoke({
    "attempt": 0,
    "max_attempts": 5,
    "success": False,
    "result": "",
    "errors": [],
    "backoff_seconds": 0
})

print(f"\nFinal result: {result['result']}")
print(f"Success: {result['success']}")
print(f"Total attempts: {result['attempt']}")
```

**Flow Diagram:**
```
START → try ←─────┐
         ↓        │
    [check]       │
         ↓        │
  failed? → wait ─┘
         ↓
   success/give_up
         ↓
        END
```

---

## 🎨 Advanced Examples

### Example 1: Self-Correcting Code Generator

**Scenario**: Code generate karo, validate karo, errors fix karo, repeat

```python
class CodeState(TypedDict):
    task_description: str
    code: str
    errors: Annotated[list[str], add]
    iteration: int
    max_iterations: int
    is_valid: bool

def generate_code(state: CodeState) -> CodeState:
    """Generate or fix code based on errors"""
    if state["iteration"] == 0:
        # Initial generation
        code = f"# Code for: {state['task_description']}\ndef solution():\n    pass"
    else:
        # Fix based on previous errors
        previous_errors = state["errors"][-3:] if state["errors"] else []
        code = state["code"] + "\n# Fixed based on errors"
    
    return {
        "code": code,
        "iteration": state["iteration"] + 1
    }

def validate_code(state: CodeState) -> CodeState:
    """Validate the generated code"""
    code = state["code"]
    errors = []
    
    # Simple validation (in real app, use actual linting/testing)
    if "pass" in code and state["iteration"] > 0:
        errors.append("Code still contains 'pass' statement")
    
    if "def solution" not in code:
        errors.append("Missing 'solution' function")
    
    is_valid = len(errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": errors if errors else []
    }

def should_continue_coding(state: CodeState) -> Literal["fix", "done"]:
    """Decide if we need more iterations"""
    if state["is_valid"]:
        return "done"
    
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    
    return "fix"

# Build graph
graph = StateGraph(CodeState)
graph.add_node("generate", generate_code)
graph.add_node("validate", validate_code)

graph.add_edge(START, "generate")
graph.add_edge("generate", "validate")
graph.add_conditional_edges(
    "validate",
    should_continue_coding,
    {
        "fix": "generate",  # Loop back to fix
        "done": END
    }
)

workflow = graph.compile()

# Run
result = workflow.invoke({
    "task_description": "Calculate factorial",
    "code": "",
    "errors": [],
    "iteration": 0,
    "max_iterations": 5,
    "is_valid": False
})

print(f"Valid: {result['is_valid']}")
print(f"Iterations: {result['iteration']}")
print(f"Code:\n{result['code']}")
```

---

### Example 2: Progressive Content Refinement

**Scenario**: Blog post ko iteratively improve karo based on feedback

```python
class ContentState(TypedDict):
    topic: str
    draft: str
    feedback: Annotated[list[str], add]
    version: int
    max_versions: int
    readability_score: float
    target_score: float

def write_draft(state: ContentState) -> ContentState:
    """Write or refine content"""
    if state["version"] == 0:
        # Initial draft
        draft = f"Blog post about {state['topic']}.\n\nIntroduction paragraph."
    else:
        # Refine based on feedback
        recent_feedback = state["feedback"][-1] if state["feedback"] else ""
        draft = state["draft"] + f"\n\n[Improved based on: {recent_feedback}]"
    
    return {
        "draft": draft,
        "version": state["version"] + 1
    }

def analyze_content(state: ContentState) -> ContentState:
    """Analyze content quality and provide feedback"""
    draft = state["draft"]
    
    # Simulate readability scoring (in real app, use actual metrics)
    word_count = len(draft.split())
    readability = min(0.4 + (word_count / 100), 1.0)
    
    # Generate feedback
    feedback = []
    if readability < 0.6:
        feedback.append("Add more detailed explanations")
    elif readability < 0.8:
        feedback.append("Include examples and use cases")
    else:
        feedback.append("Content looks good!")
    
    return {
        "readability_score": readability,
        "feedback": feedback
    }

def check_content_quality(state: ContentState) -> Literal["refine", "publish"]:
    """Decide if content is ready to publish"""
    if state["readability_score"] >= state["target_score"]:
        return "publish"
    
    if state["version"] >= state["max_versions"]:
        return "publish"
    
    return "refine"

# Build graph
graph = StateGraph(ContentState)
graph.add_node("write", write_draft)
graph.add_node("analyze", analyze_content)

graph.add_edge(START, "write")
graph.add_edge("write", "analyze")
graph.add_conditional_edges(
    "analyze",
    check_content_quality,
    {
        "refine": "write",  # Loop back to improve
        "publish": END
    }
)

workflow = graph.compile()

# Run
result = workflow.invoke({
    "topic": "Introduction to LangGraph",
    "draft": "",
    "feedback": [],
    "version": 0,
    "max_versions": 5,
    "readability_score": 0.0,
    "target_score": 0.8
})

print(f"Final version: {result['version']}")
print(f"Readability: {result['readability_score']:.2f}")
print(f"Draft:\n{result['draft']}")
```

---

### Example 3: Multi-Stage Data Processing Loop

**Scenario**: Data ko stages mein process karo, har stage ke baad validate karo

```python
class DataProcessingState(TypedDict):
    raw_data: list[dict]
    processed_data: list[dict]
    current_stage: int
    total_stages: int
    stage_results: Annotated[list[str], add]
    errors: Annotated[list[str], add]
    all_stages_complete: bool

def process_stage(state: DataProcessingState) -> DataProcessingState:
    """Process current stage"""
    stage = state["current_stage"]
    data = state["processed_data"] if state["processed_data"] else state["raw_data"]
    
    # Simulate stage processing
    if stage == 1:
        processed = [{"id": item.get("id"), "cleaned": True} for item in data]
        stage_name = "Data Cleaning"
    elif stage == 2:
        processed = [{**item, "validated": True} for item in data]
        stage_name = "Data Validation"
    elif stage == 3:
        processed = [{**item, "enriched": True} for item in data]
        stage_name = "Data Enrichment"
    else:
        processed = data
        stage_name = "Final Stage"
    
    return {
        "processed_data": processed,
        "current_stage": stage + 1,
        "stage_results": [f"Stage {stage} ({stage_name}) completed"]
    }

def validate_stage(state: DataProcessingState) -> DataProcessingState:
    """Validate stage results"""
    # Simple validation
    errors = []
    
    if not state["processed_data"]:
        errors.append("No data processed")
    
    return {
        "errors": errors if errors else [],
        "all_stages_complete": state["current_stage"] >= state["total_stages"]
    }

def should_continue_processing(state: DataProcessingState) -> Literal["next_stage", "done"]:
    """Decide if we need more stages"""
    if state["all_stages_complete"]:
        return "done"
    
    if state["errors"]:
        return "done"  # Stop on errors
    
    return "next_stage"

# Build graph
graph = StateGraph(DataProcessingState)
graph.add_node("process", process_stage)
graph.add_node("validate", validate_stage)

graph.add_edge(START, "process")
graph.add_edge("process", "validate")
graph.add_conditional_edges(
    "validate",
    should_continue_processing,
    {
        "next_stage": "process",  # Loop to next stage
        "done": END
    }
)

workflow = graph.compile()

# Run
result = workflow.invoke({
    "raw_data": [{"id": 1}, {"id": 2}, {"id": 3}],
    "processed_data": [],
    "current_stage": 1,
    "total_stages": 3,
    "stage_results": [],
    "errors": [],
    "all_stages_complete": False
})

print(f"Stages completed: {result['current_stage'] - 1}")
print(f"Results: {result['stage_results']}")
print(f"Final data: {result['processed_data']}")
```

---

## 🌍 Real-World Use Cases

### Use Case 1: Chatbot with Clarification Loop

**Problem**: User ka query unclear hai, clarification maango until clear ho jaye

```python
class ChatState(TypedDict):
    user_query: str
    clarifications: Annotated[list[str], add]
    is_clear: bool
    iteration: int
    max_iterations: int
    final_response: str

def analyze_query(state: ChatState) -> ChatState:
    """Analyze if query is clear enough"""
    query = state["user_query"]
    clarifications = state["clarifications"]
    
    # Simulate clarity check (in real app, use NLP)
    is_clear = len(clarifications) >= 2 or "specific" in query.lower()
    
    return {
        "is_clear": is_clear,
        "iteration": state["iteration"] + 1
    }

def ask_clarification(state: ChatState) -> ChatState:
    """Ask for more details"""
    clarification = f"Clarification request {state['iteration']}: Can you provide more details?"
    
    # Simulate user response (in real app, wait for actual user input)
    user_response = f"More specific details about the query"
    
    return {
        "clarifications": [clarification, user_response],
        "user_query": state["user_query"] + " " + user_response
    }

def generate_response(state: ChatState) -> ChatState:
    """Generate final response"""
    response = f"Based on your query and {len(state['clarifications'])} clarifications, here's the answer..."
    
    return {"final_response": response}

def needs_clarification(state: ChatState) -> Literal["clarify", "respond"]:
    """Check if we need more clarification"""
    if state["is_clear"]:
        return "respond"
    
    if state["iteration"] >= state["max_iterations"]:
        return "respond"  # Give up after max iterations
    
    return "clarify"

# Build graph
graph = StateGraph(ChatState)
graph.add_node("analyze", analyze_query)
graph.add_node("clarify", ask_clarification)
graph.add_node("respond", generate_response)

graph.add_edge(START, "analyze")
graph.add_conditional_edges(
    "analyze",
    needs_clarification,
    {
        "clarify": "clarify",
        "respond": "respond"
    }
)
graph.add_edge("clarify", "analyze")  # Loop back
graph.add_edge("respond", END)

workflow = graph.compile()
```

---

### Use Case 2: Code Testing & Fixing Loop

**Problem**: Code generate karo, test karo, agar fail ho to fix karo

```python
class TestingState(TypedDict):
    code: str
    test_results: Annotated[list[dict], add]
    all_tests_passed: bool
    attempt: int
    max_attempts: int

def run_tests(state: TestingState) -> TestingState:
    """Run tests on the code"""
    # Simulate test execution
    tests_passed = state["attempt"] >= 2  # Pass after 2 attempts for demo
    
    test_result = {
        "attempt": state["attempt"],
        "passed": tests_passed,
        "failures": [] if tests_passed else ["Test case 1 failed"]
    }
    
    return {
        "test_results": [test_result],
        "all_tests_passed": tests_passed
    }

def fix_code(state: TestingState) -> TestingState:
    """Fix code based on test failures"""
    last_result = state["test_results"][-1] if state["test_results"] else {}
    failures = last_result.get("failures", [])
    
    fixed_code = state["code"] + f"\n# Fixed: {', '.join(failures)}"
    
    return {
        "code": fixed_code,
        "attempt": state["attempt"] + 1
    }

def check_tests(state: TestingState) -> Literal["fix", "done"]:
    """Decide if we need to fix code"""
    if state["all_tests_passed"]:
        return "done"
    
    if state["attempt"] >= state["max_attempts"]:
        return "done"
    
    return "fix"

# Build graph
graph = StateGraph(TestingState)
graph.add_node("test", run_tests)
graph.add_node("fix", fix_code)

graph.add_edge(START, "test")
graph.add_conditional_edges(
    "test",
    check_tests,
    {
        "fix": "fix",
        "done": END
    }
)
graph.add_edge("fix", "test")  # Loop back to test again

workflow = graph.compile()
```

---

### Use Case 3: Iterative Search with Refinement

**Problem**: Search query ko refine karo jab tak relevant results na mil jayein

```python
class SearchState(TypedDict):
    original_query: str
    refined_query: str
    search_results: Annotated[list[dict], add]
    relevance_score: float
    iteration: int
    max_iterations: int
    target_relevance: float

def search(state: SearchState) -> SearchState:
    """Execute search with current query"""
    query = state["refined_query"] or state["original_query"]
    
    # Simulate search (in real app, call actual search API)
    results = [
        {"title": f"Result {i} for '{query}'", "score": 0.5 + (state["iteration"] * 0.1)}
        for i in range(3)
    ]
    
    # Calculate average relevance
    avg_score = sum(r["score"] for r in results) / len(results)
    
    return {
        "search_results": results,
        "relevance_score": avg_score,
        "iteration": state["iteration"] + 1
    }

def refine_query(state: SearchState) -> SearchState:
    """Refine search query based on results"""
    original = state["original_query"]
    iteration = state["iteration"]
    
    # Add refinements (in real app, use NLP/embeddings)
    refined = f"{original} refined_v{iteration}"
    
    return {"refined_query": refined}

def check_relevance(state: SearchState) -> Literal["refine", "done"]:
    """Check if results are relevant enough"""
    if state["relevance_score"] >= state["target_relevance"]:
        return "done"
    
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    
    return "refine"

# Build graph
graph = StateGraph(SearchState)
graph.add_node("search", search)
graph.add_node("refine", refine_query)

graph.add_edge(START, "search")
graph.add_conditional_edges(
    "search",
    check_relevance,
    {
        "refine": "refine",
        "done": END
    }
)
graph.add_edge("refine", "search")  # Loop back

workflow = graph.compile()
```

---

## ✅ Best Practices

### 1. Always Set Maximum Iterations

**DO:**
```python
class SafeState(TypedDict):
    counter: int
    max_iterations: int  # ✅ Always have a limit

def should_continue(state: SafeState) -> Literal["continue", "end"]:
    if state["counter"] >= state["max_iterations"]:
        return "end"  # ✅ Guaranteed exit
    return "continue"
```

**DON'T:**
```python
def unsafe_continue(state) -> Literal["continue", "end"]:
    if some_condition:  # ❌ What if condition never becomes true?
        return "end"
    return "continue"
```

### 2. Track Progress Clearly

**DO:**
```python
class TrackedState(TypedDict):
    iteration: int
    history: Annotated[list[dict], add]  # ✅ Track each iteration
    
def process(state: TrackedState) -> TrackedState:
    return {
        "iteration": state["iteration"] + 1,
        "history": [{
            "iteration": state["iteration"],
            "timestamp": time.time(),
            "result": "..."
        }]
    }
```

### 3. Provide Multiple Exit Conditions

**DO:**
```python
def smart_exit(state: MyState) -> Literal["continue", "success", "timeout", "error"]:
    # ✅ Multiple exit paths
    if state["success"]:
        return "success"
    elif state["iteration"] >= state["max_iterations"]:
        return "timeout"
    elif state["errors"]:
        return "error"
    else:
        return "continue"
```

### 4. Use Meaningful State Updates

**DO:**
```python
def meaningful_update(state: MyState) -> MyState:
    return {
        "result": computed_result,
        "iteration": state["iteration"] + 1,
        "last_update": datetime.now().isoformat(),  # ✅ Useful metadata
        "improvement": new_score - old_score  # ✅ Track progress
    }
```

### 5. Log Each Iteration

**DO:**
```python
def logged_process(state: MyState) -> MyState:
    iteration = state["iteration"] + 1
    print(f"[Iteration {iteration}] Processing...")  # ✅ Visibility
    
    result = do_processing(state)
    
    print(f"[Iteration {iteration}] Score: {result['score']}")  # ✅ Progress
    return result
```

### 6. Handle Edge Cases

**DO:**
```python
def robust_check(state: MyState) -> Literal["continue", "end"]:
    # ✅ Handle missing/invalid data
    if not state.get("data"):
        return "end"
    
    # ✅ Handle division by zero
    if state.get("denominator", 0) == 0:
        return "end"
    
    # Normal logic
    return "continue" if state["counter"] < 10 else "end"
```

---

## ⚠️ Common Pitfalls

### Pitfall 1: Infinite Loops

**Problem:**
```python
# ❌ No exit condition!
def bad_loop(state) -> Literal["continue"]:
    return "continue"  # Runs forever!
```

**Solution:**
```python
# ✅ Always have exit
def good_loop(state) -> Literal["continue", "end"]:
    if state["counter"] >= state["max"]:
        return "end"
    return "continue"
```

### Pitfall 2: Not Updating Loop Counter

**Problem:**
```python
def forgot_increment(state: MyState) -> MyState:
    # ❌ Counter never increments!
    return {"result": "..."}
```

**Solution:**
```python
def remember_increment(state: MyState) -> MyState:
    # ✅ Always increment
    return {
        "result": "...",
        "counter": state["counter"] + 1
    }
```

### Pitfall 3: Accumulating Without Reducer

**Problem:**
```python
class BadState(TypedDict):
    results: list  # ❌ Will be overwritten, not accumulated!

def add_result(state: BadState) -> BadState:
    return {"results": [new_result]}  # ❌ Loses previous results
```

**Solution:**
```python
class GoodState(TypedDict):
    results: Annotated[list, add]  # ✅ Accumulates!

def add_result(state: GoodState) -> GoodState:
    return {"results": [new_result]}  # ✅ Appends to list
```

### Pitfall 4: Complex Exit Logic

**Problem:**
```python
def confusing_exit(state) -> Literal["a", "b", "c", "d"]:
    # ❌ Too many branches, hard to debug
    if condition1 and condition2 or condition3:
        if nested_condition:
            return "a"
        else:
            return "b"
    # ... more complexity
```

**Solution:**
```python
def clear_exit(state) -> Literal["continue", "end"]:
    # ✅ Simple, clear logic
    should_stop = (
        state["counter"] >= state["max"] or
        state["quality"] >= state["target"] or
        bool(state["errors"])
    )
    return "end" if should_stop else "continue"
```

---

## 🔧 Troubleshooting

### Problem 1: Loop Runs Forever

**Symptoms:** Workflow never completes

**Debug Steps:**
```python
def debug_continue(state: MyState) -> Literal["continue", "end"]:
    print(f"Counter: {state['counter']}, Max: {state['max_iterations']}")  # Add logging
    
    if state["counter"] >= state["max_iterations"]:
        print("Exiting due to max iterations")  # Confirm exit
        return "end"
    
    print("Continuing...")
    return "continue"
```

**Common Causes:**
- Counter not incrementing
- Exit condition never true
- Wrong comparison operator (`>` instead of `>=`)

### Problem 2: State Not Accumulating

**Symptoms:** Lists/arrays not growing across iterations

**Solution:**
```python
# ✅ Use Annotated with reducer
from typing import Annotated
from operator import add

class FixedState(TypedDict):
    items: Annotated[list[str], add]  # This will accumulate!
```

### Problem 3: Too Many Iterations

**Symptoms:** Loop runs max iterations but doesn't achieve goal

**Solutions:**
- Increase `max_iterations`
- Improve processing logic
- Add better exit conditions
- Check if goal is achievable

```python
def better_exit(state: MyState) -> Literal["continue", "end"]:
    # ✅ Multiple success conditions
    if state["quality"] >= state["target"]:
        return "end"  # Success!
    
    if state["counter"] >= state["max_iterations"]:
        print(f"Warning: Max iterations reached. Quality: {state['quality']}")
        return "end"  # Timeout
    
    return "continue"
```

---

## 📊 Complete Projects

### Project 1: Blog Post Generator with Iterative Refinement

Complete example with LLM integration:

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Annotated
from operator import add

class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: Annotated[list[str], add]
    version: int
    max_versions: int
    word_count: int
    target_words: int
    quality_score: float

def generate_draft(state: BlogState) -> BlogState:
    """Generate or refine blog draft"""
    if state["version"] == 0:
        # Initial draft
        draft = f"""# {state['topic']}

## Introduction
This is an introduction to {state['topic']}.

## Main Content
Here we discuss the key points about {state['topic']}.

## Conclusion
In conclusion, {state['topic']} is important.
"""
    else:
        # Refine based on feedback
        last_feedback = state["feedback"][-1] if state["feedback"] else ""
        draft = state["draft"] + f"\n\n## Additional Section\nAddressing: {last_feedback}"
    
    word_count = len(draft.split())
    
    return {
        "draft": draft,
        "version": state["version"] + 1,
        "word_count": word_count
    }

def evaluate_draft(state: BlogState) -> BlogState:
    """Evaluate draft quality and provide feedback"""
    word_count = state["word_count"]
    target = state["target_words"]
    
    # Calculate quality score
    word_ratio = min(word_count / target, 1.0)
    quality = word_ratio * 0.7 + 0.3  # Base quality + word count factor
    
    # Generate feedback
    feedback = []
    if word_count < target * 0.8:
        feedback.append("Add more detailed examples and explanations")
    elif word_count < target:
        feedback.append("Include use cases and best practices")
    else:
        feedback.append("Content length is good!")
    
    return {
        "quality_score": quality,
        "feedback": feedback
    }

def should_refine(state: BlogState) -> Literal["refine", "publish"]:
    """Decide if we need more refinement"""
    if state["quality_score"] >= 0.9:
        return "publish"
    
    if state["version"] >= state["max_versions"]:
        return "publish"
    
    return "refine"

# Build workflow
graph = StateGraph(BlogState)
graph.add_node("generate", generate_draft)
graph.add_node("evaluate", evaluate_draft)

graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    should_refine,
    {
        "refine": "generate",
        "publish": END
    }
)

blog_workflow = graph.compile()

# Run
result = blog_workflow.invoke({
    "topic": "Introduction to LangGraph Iterative Workflows",
    "draft": "",
    "feedback": [],
    "version": 0,
    "max_versions": 5,
    "word_count": 0,
    "target_words": 500,
    "quality_score": 0.0
})

print(f"Final version: {result['version']}")
print(f"Word count: {result['word_count']}")
print(f"Quality score: {result['quality_score']:.2f}")
print(f"\nFinal draft:\n{result['draft']}")
```

---

### Project 2: Data Cleaning Pipeline with Validation Loop

```python
class CleaningState(TypedDict):
    raw_data: list[dict]
    cleaned_data: list[dict]
    validation_errors: Annotated[list[str], add]
    cleaning_iteration: int
    max_iterations: int
    is_valid: bool

def clean_data(state: CleaningState) -> CleaningState:
    """Clean data based on previous validation errors"""
    data = state["raw_data"] if state["cleaning_iteration"] == 0 else state["cleaned_data"]
    
    cleaned = []
    for item in data:
        cleaned_item = {}
        
        # Clean each field
        if "email" in item:
            cleaned_item["email"] = item["email"].strip().lower()
        
        if "age" in item:
            try:
                cleaned_item["age"] = int(item["age"])
            except:
                cleaned_item["age"] = None
        
        if "name" in item:
            cleaned_item["name"] = item["name"].strip().title()
        
        cleaned.append(cleaned_item)
    
    return {
        "cleaned_data": cleaned,
        "cleaning_iteration": state["cleaning_iteration"] + 1
    }

def validate_data(state: CleaningState) -> CleaningState:
    """Validate cleaned data"""
    errors = []
    
    for i, item in enumerate(state["cleaned_data"]):
        # Validate email
        if "email" in item and "@" not in item["email"]:
            errors.append(f"Row {i}: Invalid email format")
        
        # Validate age
        if "age" in item and (item["age"] is None or item["age"] < 0 or item["age"] > 150):
            errors.append(f"Row {i}: Invalid age")
        
        # Validate name
        if "name" in item and not item["name"]:
            errors.append(f"Row {i}: Missing name")
    
    is_valid = len(errors) == 0
    
    return {
        "validation_errors": errors if errors else [],
        "is_valid": is_valid
    }

def should_reclean(state: CleaningState) -> Literal["clean", "done"]:
    """Decide if we need another cleaning pass"""
    if state["is_valid"]:
        return "done"
    
    if state["cleaning_iteration"] >= state["max_iterations"]:
        return "done"
    
    return "clean"

# Build workflow
graph = StateGraph(CleaningState)
graph.add_node("clean", clean_data)
graph.add_node("validate", validate_data)

graph.add_edge(START, "clean")
graph.add_edge("clean", "validate")
graph.add_conditional_edges(
    "validate",
    should_reclean,
    {
        "clean": "clean",
        "done": END
    }
)

cleaning_workflow = graph.compile()

# Run
test_data = [
    {"email": " TEST@EXAMPLE.COM ", "age": "25", "name": "john doe"},
    {"email": "invalid-email", "age": "-5", "name": ""},
    {"email": "valid@test.com", "age": "30", "name": " jane smith "}
]

result = cleaning_workflow.invoke({
    "raw_data": test_data,
    "cleaned_data": [],
    "validation_errors": [],
    "cleaning_iteration": 0,
    "max_iterations": 3,
    "is_valid": False
})

print(f"Valid: {result['is_valid']}")
print(f"Iterations: {result['cleaning_iteration']}")
print(f"Errors: {result['validation_errors']}")
print(f"Cleaned data: {result['cleaned_data']}")
```

---

## 📚 Summary

### Key Takeaways

1. **Iterative workflows** loops aur cycles enable karte hain
2. **Always set max_iterations** to prevent infinite loops
3. **Use Annotated[list, add]** for accumulating state
4. **Multiple exit conditions** flexibility provide karte hain
5. **Track progress** with counters and history
6. **Log each iteration** for debugging

### Pattern Comparison

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| Simple Counter | Basic iteration | ⭐ Easy |
| Quality-Based | Progressive improvement | ⭐⭐ Medium |
| Retry Logic | Error recovery | ⭐⭐ Medium |
| Self-Correction | Automated fixing | ⭐⭐⭐ Advanced |
| Multi-Stage | Complex pipelines | ⭐⭐⭐ Advanced |

### When to Use Iterative Workflows

✅ **Use when:**
- Need progressive improvement
- Implementing retry logic
- Self-correction required
- Multi-pass processing
- Quality thresholds

❌ **Don't use when:**
- Simple one-time operation
- Independent parallel tasks
- Simple branching logic
- Deterministic single-pass

---

## 🎓 Next Steps

1. ✅ Practice basic counter loop
2. ✅ Implement quality-based iteration
3. ✅ Add retry logic to existing workflow
4. ✅ Build self-correcting system
5. ✅ Create production-ready iterative workflow

---

**Happy Iterating! 🔄**

*Guide created: January 2026*  
*Version: 1.0*  
*Language: Roman Urdu*

