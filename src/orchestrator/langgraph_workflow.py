# src/orchestrator/langgraph_workflow.py
"""Orchestrator wiring for the multi-agent pipeline.

This module prefers LangGraph if available; if not, it falls back to a
simple sequential runner that invokes the research -> analysis -> write nodes.
"""
try:
    from langgraph.graph import StateGraph, MessagesState, START, END  # type: ignore
    HAS_LANGGRAPH = True
except Exception:
    StateGraph = None
    MessagesState = dict
    START = "__start__"
    END = "__end__"
    HAS_LANGGRAPH = False

from src.agents.research_agent import research_topic
from src.agents.analysis_agent import analyze_research
from src.agents.report_writer_agent import write_report
from pathlib import Path
import pprint


# -------------------------
# Node functions
# -------------------------
def node_research(state):
    # state can be dict in latest LangGraph
    topic = state.get("topic", "")
    try:
        research = research_topic(
            topic, max_results=state.get("max_results", 5))
        if not research:
            research = {"query": topic, "hits": [], "excerpts": [
                "No excerpts found."], "summary": "No summary."}
    except Exception as e:
        research = {"query": topic, "hits": [], "excerpts": [
            "Error occurred."], "summary": str(e)}
        if isinstance(state, dict):
            state.setdefault("_messages", []).append(
                f"Research node error: {e}")
        else:
            state.add_message(f"Research node error: {e}")

    if isinstance(state, dict):
        state["research"] = research
    else:
        state.set("research", research)

    print("\n[DEBUG] Research Node Output:")
    pprint.pprint(research)
    return state


def node_analysis(state):
    research = state.get(
        "research", {"excerpts": ["No excerpts found."], "summary": ""})
    try:
        structured = analyze_research(research)
        if not structured:
            structured = {
                "title": research.get("query", "Untitled Report"),
                "summary": research.get("summary", ""),
                "sections": [{"heading": "Key Points", "content": research.get("excerpts", [])}]
            }
    except Exception as e:
        structured = {
            "title": research.get("query", "Untitled Report"),
            "summary": research.get("summary", ""),
            "sections": [{"heading": "Error", "content": str(e)}]
        }
        if isinstance(state, dict):
            state.setdefault("_messages", []).append(
                f"Analysis node error: {e}")
        else:
            state.add_message(f"Analysis node error: {e}")

    if isinstance(state, dict):
        state["structured"] = structured
    else:
        state.set("structured", structured)

    print("\n[DEBUG] Analysis Node Output:")
    pprint.pprint(structured)
    return state


def node_write(state):
    structured = state.get("structured", {
        "title": "Untitled Report",
        "sections": [{"heading": "Empty", "content": "No content available."}]
    })
    try:
        output = write_report(structured)
        # Convert Path to str
        for key, val in output.items():
            if isinstance(val, Path):
                output[key] = str(val)
        if not output:
            output = {"error": "Report generation returned empty output."}
    except Exception as e:
        output = {"error": str(e)}
        if isinstance(state, dict):
            state.setdefault("_messages", []).append(f"Write node error: {e}")
        else:
            state.add_message(f"Write node error: {e}")

    if isinstance(state, dict):
        state["output_paths"] = output
    else:
        state.set("output_paths", output)

    print("\n[DEBUG] Write Node Output:")
    pprint.pprint(output)
    return state

# -------------------------
# Build graph
# -------------------------


def build_graph():
    if HAS_LANGGRAPH and StateGraph is not None:
        graph = StateGraph(MessagesState)
        graph.add_node("research", node_research)
        graph.add_node("analysis", node_analysis)
        graph.add_node("write", node_write)

        graph.add_edge(START, "research")
        graph.add_edge("research", "analysis")
        graph.add_edge("analysis", "write")
        graph.add_edge("write", END)

        return graph.compile()

    # Fallback simple sequential graph
    class SimpleGraph:
        def __init__(self):
            self._nodes = [("research", node_research),
                           ("analysis", node_analysis), ("write", node_write)]

        def invoke(self, state):
            # Execute nodes in order; nodes may mutate the dict state
            for name, fn in self._nodes:
                try:
                    state = fn(state)
                except Exception as e:
                    # attach message and continue
                    if isinstance(state, dict):
                        state.setdefault("_messages", []).append(
                            f"{name} node error: {e}")
            return state

    return SimpleGraph()


_graph = build_graph()

# -------------------------
# Run workflow
# -------------------------


def run_workflow(topic: str, max_results: int = 5) -> dict:
    # Use a simple dict for input (latest LangGraph)
    state = {
        "topic": topic,
        "max_results": max_results,
        "_messages": [f"Start research for {topic}"]
    }

    # Try to invoke the compiled graph. If LangGraph returns an unexpected
    # state (e.g., it wraps or drops our dict), fall back to a local sequential
    # execution of the nodes to guarantee correct behavior.
    try:
        final_state = _graph.invoke(state)
    except Exception:
        final_state = None

    # If final_state looks wrong, run nodes sequentially to ensure state flows
    if not isinstance(final_state, dict) or (isinstance(final_state, dict) and not final_state.get("research") and not final_state.get("output_paths")):
        # start from fresh state dict and execute nodes manually
        state = {
            "topic": topic,
            "max_results": max_results,
            "_messages": [f"Start research for {topic}"]
        }
        state = node_research(state)
        state = node_analysis(state)
        state = node_write(state)
        final_state = state

    print("\n[DEBUG] Final Workflow State:")
    pprint.pprint(final_state)

    # Ensure all Path objects are strings
    output_paths = {}
    for key, val in final_state.get("output_paths", {}).items():
        if isinstance(val, Path):
            output_paths[key] = str(val)
        else:
            output_paths[key] = val

    return output_paths if output_paths else {"error": "no output"}
