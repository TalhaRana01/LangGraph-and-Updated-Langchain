"""
=============================================================================
LANGGRAPH FOUNDATION - COMPLETE GUIDE
=============================================================================

LangGraph ek powerful framework hai jo complex AI workflows banane ke liye 
use hota hai. Yeh stateful, multi-actor applications create karne mein help 
karta hai with cycles aur controllability.

Author: Complete Foundation Guide
Date: January 2026
=============================================================================
"""

# =============================================================================
# SECTION 1: CORE CONCEPTS
# =============================================================================

"""
1. STATE (حالت):
   - Graph ki current condition ko represent karta hai
   - TypedDict ya Pydantic models use kar ke define hota hai
   - Har node state ko read aur update kar sakta hai

2. NODES (نوڈز):
   - Functions jo state ko process karte hain
   - Input: current state
   - Output: state updates (dictionary)

3. EDGES (کنارے):
   - Nodes ke beech connections
   - Control flow define karte hain
   - Types: Normal edges, Conditional edges

4. GRAPH (گراف):
   - Nodes aur edges ka collection
   - StateGraph class se create hota hai
   - Compile karne ke baad executable workflow ban jata hai

5. START & END:
   - START: Entry point of workflow
   - END: Exit point of workflow
"""

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

def summary_node(state: ParallelState) -> ParallelState:
    """Create summary"""
    print(f"  -> Creating summary...")
    summary = f"Input: {state['input_value']}, Square: {state['squared']}, Cube: {state['cubed']}, Double: {state['doubled']}"
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

# =============================================================================
# SECTION 6: EXAMPLE 4 - STATE WITH REDUCERS (ACCUMULATION)
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 4: STATE WITH REDUCERS (LIST ACCUMULATION)")
print("="*80)

class AccumulatorState(TypedDict):
    """State with list accumulation using Annotated"""
    messages: Annotated[list[str], operator.add]  # Will accumulate messages
    count: int

def add_message_1(state: AccumulatorState) -> AccumulatorState:
    """Add first message"""
    print(f"  -> Adding message 1")
    return {"messages": ["First message"], "count": 1}

def add_message_2(state: AccumulatorState) -> AccumulatorState:
    """Add second message"""
    print(f"  -> Adding message 2")
    return {"messages": ["Second message"], "count": 2}

def add_message_3(state: AccumulatorState) -> AccumulatorState:
    """Add third message"""
    print(f"  -> Adding message 3")
    return {"messages": ["Third message"], "count": 3}

# Create accumulator graph
accumulator_graph = StateGraph(AccumulatorState)
accumulator_graph.add_node("msg1", add_message_1)
accumulator_graph.add_node("msg2", add_message_2)
accumulator_graph.add_node("msg3", add_message_3)

# Sequential edges
accumulator_graph.add_edge(START, "msg1")
accumulator_graph.add_edge("msg1", "msg2")
accumulator_graph.add_edge("msg2", "msg3")
accumulator_graph.add_edge("msg3", END)

# Compile and execute
accumulator_workflow = accumulator_graph.compile()
result = accumulator_workflow.invoke({"messages": [], "count": 0})
print(f"\n✅ Result: {result}")
print(f"✅ All messages accumulated: {result['messages']}")

# =============================================================================
# SECTION 7: EXAMPLE 5 - LOOP/CYCLE WORKFLOW
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 5: LOOP/CYCLE WORKFLOW")
print("="*80)

class LoopState(TypedDict):
    """State for loop example"""
    counter: int
    max_iterations: int
    results: Annotated[list[int], operator.add]

def increment_node(state: LoopState) -> LoopState:
    """Increment counter"""
    new_counter = state["counter"] + 1
    print(f"  -> Iteration {new_counter}")
    return {
        "counter": new_counter,
        "results": [new_counter]
    }

def should_continue(state: LoopState) -> Literal["continue", "end"]:
    """Decide whether to continue loop"""
    if state["counter"] < state["max_iterations"]:
        print(f"  -> Continuing loop (counter: {state['counter']})")
        return "continue"
    else:
        print(f"  -> Ending loop (reached max: {state['max_iterations']})")
        return "end"

# Create loop graph
loop_graph = StateGraph(LoopState)
loop_graph.add_node("increment", increment_node)

# Add edges
loop_graph.add_edge(START, "increment")

# Conditional edge that creates a loop
loop_graph.add_conditional_edges(
    "increment",
    should_continue,
    {
        "continue": "increment",  # Loop back to increment
        "end": END
    }
)

# Compile and execute
loop_workflow = loop_graph.compile()
result = loop_workflow.invoke({"counter": 0, "max_iterations": 5, "results": []})
print(f"\n✅ Final Result: {result}")

# =============================================================================
# SECTION 8: ERROR HANDLING PATTERNS
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 6: ERROR HANDLING")
print("="*80)

class ErrorState(TypedDict):
    """State with error handling"""
    input_value: int
    result: int
    error: str
    status: str

def risky_operation(state: ErrorState) -> ErrorState:
    """Operation that might fail"""
    try:
        print(f"  -> Attempting risky operation with value: {state['input_value']}")
        
        # Simulate error for negative numbers
        if state["input_value"] < 0:
            raise ValueError("Negative numbers not allowed!")
        
        result = 100 / state["input_value"]
        return {
            "result": result,
            "status": "success",
            "error": ""
        }
    
    except ZeroDivisionError as e:
        print(f"  ❌ Error: Division by zero")
        return {
            "result": 0,
            "status": "error",
            "error": "Cannot divide by zero"
        }
    
    except ValueError as e:
        print(f"  ❌ Error: {str(e)}")
        return {
            "result": 0,
            "status": "error",
            "error": str(e)
        }
    
    except Exception as e:
        print(f"  ❌ Unexpected error: {str(e)}")
        return {
            "result": 0,
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }

def handle_success(state: ErrorState) -> ErrorState:
    """Handle successful operation"""
    print(f"  ✅ Success! Result: {state['result']}")
    return {"status": "completed"}

def handle_error(state: ErrorState) -> ErrorState:
    """Handle error"""
    print(f"  🔧 Handling error: {state['error']}")
    return {"status": "failed"}

def route_by_status(state: ErrorState) -> Literal["success", "error"]:
    """Route based on operation status"""
    return state["status"]

# Create error handling graph
error_graph = StateGraph(ErrorState)
error_graph.add_node("operation", risky_operation)
error_graph.add_node("success", handle_success)
error_graph.add_node("error", handle_error)

# Add edges
error_graph.add_edge(START, "operation")
error_graph.add_conditional_edges(
    "operation",
    route_by_status,
    {
        "success": "success",
        "error": "error"
    }
)
error_graph.add_edge("success", END)
error_graph.add_edge("error", END)

# Compile and test
error_workflow = error_graph.compile()

print("\nTest 1: Valid input")
result1 = error_workflow.invoke({"input_value": 10, "result": 0, "error": "", "status": ""})
print(f"Result: {result1}\n")

print("Test 2: Division by zero")
result2 = error_workflow.invoke({"input_value": 0, "result": 0, "error": "", "status": ""})
print(f"Result: {result2}\n")

print("Test 3: Negative number")
result3 = error_workflow.invoke({"input_value": -5, "result": 0, "error": "", "status": ""})
print(f"Result: {result3}")

# =============================================================================
# SECTION 9: REAL-WORLD EXAMPLE - DATA PROCESSING PIPELINE
# =============================================================================

print("\n" + "="*80)
print("EXAMPLE 7: DATA PROCESSING PIPELINE")
print("="*80)

class DataPipelineState(TypedDict):
    """State for data processing pipeline"""
    raw_data: str
    cleaned_data: str
    validated: bool
    processed_data: dict
    errors: Annotated[list[str], operator.add]

def load_data(state: DataPipelineState) -> DataPipelineState:
    """Load raw data"""
    print(f"  -> Loading data...")
    return {"raw_data": "  user@example.com, 25, active  "}

def clean_data(state: DataPipelineState) -> DataPipelineState:
    """Clean the data"""
    print(f"  -> Cleaning data...")
    cleaned = state["raw_data"].strip()
    return {"cleaned_data": cleaned}

def validate_data(state: DataPipelineState) -> DataPipelineState:
    """Validate data format"""
    print(f"  -> Validating data...")
    parts = state["cleaned_data"].split(",")
    
    if len(parts) != 3:
        return {
            "validated": False,
            "errors": ["Invalid data format: expected 3 fields"]
        }
    
    email, age, status = [p.strip() for p in parts]
    
    if "@" not in email:
        return {
            "validated": False,
            "errors": ["Invalid email format"]
        }
    
    try:
        age_int = int(age)
        if age_int < 0 or age_int > 150:
            return {
                "validated": False,
                "errors": ["Age out of valid range"]
            }
    except ValueError:
        return {
            "validated": False,
            "errors": ["Age must be a number"]
        }
    
    return {"validated": True}

def process_data(state: DataPipelineState) -> DataPipelineState:
    """Process validated data"""
    print(f"  -> Processing data...")
    parts = state["cleaned_data"].split(",")
    email, age, status = [p.strip() for p in parts]
    
    processed = {
        "email": email,
        "age": int(age),
        "status": status,
        "category": "adult" if int(age) >= 18 else "minor"
    }
    
    return {"processed_data": processed}

def handle_invalid_data(state: DataPipelineState) -> DataPipelineState:
    """Handle validation failure"""
    print(f"  ❌ Data validation failed")
    return {"processed_data": {}}

def route_validation(state: DataPipelineState) -> Literal["valid", "invalid"]:
    """Route based on validation result"""
    return "valid" if state["validated"] else "invalid"

# Create pipeline graph
pipeline_graph = StateGraph(DataPipelineState)
pipeline_graph.add_node("load", load_data)
pipeline_graph.add_node("clean", clean_data)
pipeline_graph.add_node("validate", validate_data)
pipeline_graph.add_node("process", process_data)
pipeline_graph.add_node("handle_invalid", handle_invalid_data)

# Add edges
pipeline_graph.add_edge(START, "load")
pipeline_graph.add_edge("load", "clean")
pipeline_graph.add_edge("clean", "validate")

pipeline_graph.add_conditional_edges(
    "validate",
    route_validation,
    {
        "valid": "process",
        "invalid": "handle_invalid"
    }
)

pipeline_graph.add_edge("process", END)
pipeline_graph.add_edge("handle_invalid", END)

# Compile and execute
pipeline_workflow = pipeline_graph.compile()
result = pipeline_workflow.invoke({
    "raw_data": "",
    "cleaned_data": "",
    "validated": False,
    "processed_data": {},
    "errors": []
})

print(f"\n✅ Pipeline Result:")
print(f"   Processed Data: {result['processed_data']}")
print(f"   Errors: {result['errors']}")

# =============================================================================
# SECTION 10: BEST PRACTICES & TIPS
# =============================================================================

print("\n" + "="*80)
print("BEST PRACTICES & TIPS")
print("="*80)

best_practices = """
1. STATE DESIGN:
   ✅ Keep state minimal - sirf zaroori fields rakhen
   ✅ Use TypedDict for type safety
   ✅ Use Annotated with reducers for accumulation (lists, etc.)
   ✅ Initialize all fields properly

2. NODE FUNCTIONS:
   ✅ Keep nodes focused - ek kaam ek node
   ✅ Always return a dictionary with state updates
   ✅ Handle errors gracefully with try-except
   ✅ Add logging/print statements for debugging

3. GRAPH STRUCTURE:
   ✅ Start simple, then add complexity
   ✅ Use parallel edges jahan possible (performance)
   ✅ Conditional edges for routing logic
   ✅ Avoid unnecessary cycles (infinite loops)

4. ERROR HANDLING:
   ✅ Try-except blocks in nodes
   ✅ Error state field for tracking issues
   ✅ Separate error handling nodes
   ✅ Graceful degradation

5. TESTING:
   ✅ Test each node independently
   ✅ Test different paths through graph
   ✅ Test edge cases and errors
   ✅ Use print statements for debugging

6. PERFORMANCE:
   ✅ Use parallel edges for independent operations
   ✅ Keep state size reasonable
   ✅ Avoid deep nesting
   ✅ Profile for bottlenecks

7. DEBUGGING:
   ✅ Use workflow.get_graph() to visualize
   ✅ Add print statements in nodes
   ✅ Check state at each step
   ✅ Use try-except for error tracking
"""

print(best_practices)

# =============================================================================
# SECTION 11: COMMON PATTERNS
# =============================================================================

print("\n" + "="*80)
print("COMMON PATTERNS")
print("="*80)

patterns = """
PATTERN 1: FAN-OUT / FAN-IN (Parallel Processing)
   START → [Node1, Node2, Node3] → Aggregator → END
   Use case: Independent calculations that need to be combined

PATTERN 2: CONDITIONAL ROUTING
   START → Classifier → [PathA, PathB, PathC] → END
   Use case: Different handling based on input type/category

PATTERN 3: SEQUENTIAL PIPELINE
   START → Step1 → Step2 → Step3 → END
   Use case: Data transformation pipelines

PATTERN 4: LOOP/ITERATION
   START → Process → Check → [Continue → Process, Done → END]
   Use case: Iterative refinement, batch processing

PATTERN 5: ERROR RECOVERY
   START → TryOperation → [Success → END, Error → Retry → TryOperation]
   Use case: Resilient operations with retry logic

PATTERN 6: MAP-REDUCE
   START → Split → [Process1, Process2, ...] → Combine → END
   Use case: Parallel processing of data chunks

PATTERN 7: HUMAN-IN-THE-LOOP
   START → AutoProcess → HumanReview → [Approve → END, Reject → Revise]
   Use case: Workflows requiring human approval
"""

print(patterns)

# =============================================================================
# SECTION 12: ARCHITECTURE OVERVIEW
# =============================================================================

print("\n" + "="*80)
print("LANGGRAPH ARCHITECTURE")
print("="*80)

architecture = """
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────┘

1. STATE LAYER (حالت کی تہہ)
   ├── TypedDict/Pydantic Models
   ├── State Schema Definition
   ├── Reducers (for accumulation)
   └── Initial State

2. NODE LAYER (نوڈ کی تہہ)
   ├── Processing Functions
   ├── Business Logic
   ├── External API Calls
   └── Data Transformations

3. EDGE LAYER (کنارے کی تہہ)
   ├── Normal Edges (direct connections)
   ├── Conditional Edges (routing logic)
   └── Entry/Exit Points (START/END)

4. GRAPH LAYER (گراف کی تہہ)
   ├── StateGraph (main container)
   ├── Node Registration
   ├── Edge Configuration
   └── Compilation

5. EXECUTION LAYER (عمل کی تہہ)
   ├── Workflow Invocation
   ├── State Management
   ├── Node Execution
   └── Result Collection

FLOW:
   Input → StateGraph → Nodes (process) → Edges (route) → Output

KEY COMPONENTS:
   • StateGraph: Main graph container
   • Nodes: Processing units (functions)
   • Edges: Connections between nodes
   • State: Shared data structure
   • Reducers: State update strategies
   • Conditional Edges: Dynamic routing
"""

print(architecture)

# =============================================================================
# SECTION 13: TROUBLESHOOTING GUIDE
# =============================================================================

print("\n" + "="*80)
print("TROUBLESHOOTING GUIDE")
print("="*80)

troubleshooting = """
COMMON ISSUES & SOLUTIONS:

❌ Issue 1: "KeyError in state"
   ✅ Solution: Initialize all state fields in TypedDict
   ✅ Check node return values have correct keys

❌ Issue 2: "Infinite loop in graph"
   ✅ Solution: Add proper exit conditions in conditional edges
   ✅ Add max_iterations check in loop state

❌ Issue 3: "Node not executing"
   ✅ Solution: Check edge connections
   ✅ Verify node is added to graph
   ✅ Check conditional routing logic

❌ Issue 4: "State not updating"
   ✅ Solution: Ensure node returns dictionary
   ✅ Check if using reducer correctly
   ✅ Verify state field names match

❌ Issue 5: "Type errors"
   ✅ Solution: Use TypedDict properly
   ✅ Match return types with state schema
   ✅ Use Annotated for reducers

❌ Issue 6: "Graph compilation fails"
   ✅ Solution: Check all nodes are connected
   ✅ Verify START and END are used correctly
   ✅ Check conditional edge mappings

DEBUGGING TIPS:
   1. Add print statements in each node
   2. Check state at each step
   3. Visualize graph with get_graph()
   4. Test nodes independently first
   5. Use try-except blocks
   6. Start simple, add complexity gradually
"""

print(troubleshooting)

# =============================================================================
# SECTION 14: SUMMARY & NEXT STEPS
# =============================================================================

print("\n" + "="*80)
print("SUMMARY & NEXT STEPS")
print("="*80)

summary = """
🎯 KEY TAKEAWAYS:

1. LangGraph stateful workflows banane ke liye perfect hai
2. State, Nodes, Edges - teen main components hain
3. Parallel processing ke liye fan-out/fan-in pattern use karen
4. Conditional edges se dynamic routing implement karen
5. Reducers se lists aur values accumulate karen
6. Error handling har production workflow mein zaroori hai
7. Start simple, gradually complexity add karen

📚 NEXT STEPS:

1. LLM Integration:
   - OpenAI/Anthropic APIs integrate karen
   - Chat workflows banayein
   - RAG (Retrieval Augmented Generation) implement karen

2. Advanced Features:
   - Checkpointing (state persistence)
   - Human-in-the-loop workflows
   - Streaming responses
   - Sub-graphs

3. Production Deployment:
   - Error handling strengthen karen
   - Logging add karen
   - Monitoring setup karen
   - Testing comprehensive karen

4. Real Projects:
   - Chatbot with memory
   - Document processing pipeline
   - Multi-agent systems
   - Automated workflows

🔗 RESOURCES:
   - LangGraph Docs: https://langchain-ai.github.io/langgraph/
   - Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
   - Discord Community: LangChain Discord
"""

print(summary)

print("\n" + "="*80)
print("✅ LANGGRAPH FOUNDATION GUIDE COMPLETE!")
print("="*80)
print("\nYeh file save kar lein aur reference ke liye use karen.")
print("Happy coding! 🚀")

