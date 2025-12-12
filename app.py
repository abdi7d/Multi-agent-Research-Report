# # app.py
# import gradio as gr
# from src.orchestrator.langgraph_workflow import run_workflow
# import threading
# import time
# import os

# def run_task(topic, max_results):
#     # Blocking call that runs the LangGraph workflow and returns final paths
#     try:
#         return run_workflow(topic, int(max_results))
#     except Exception as e:
#         return {"error": str(e)}

# def submit_topic(topic, max_results=5):
#     # Kick off the workflow (run synchronously for now) and return results
#     res = run_task(topic, max_results)
#     return res

# with gr.Blocks() as demo:
#     gr.Markdown("# Multi-Agent Research & Report Generator")
#     with gr.Row():
#         topic_input = gr.Textbox(label="Research Topic", placeholder="E.g., 'Climate change impacts on Ethiopian agriculture'")
#         max_results = gr.Number(value=5, label="Maximum search results")
#     run_btn = gr.Button("Run Research Workflow")
#     output = gr.JSON(label="Result (paths / messages)")

#     run_btn.click(fn=submit_topic, inputs=[topic_input, max_results], outputs=output)

# demo.launch()










import gradio as gr
from src.orchestrator.langgraph_workflow import run_workflow
from pathlib import Path

def generate_report(topic: str):
    paths = run_workflow(topic)
    if "error" in paths:
        return paths["error"], None, None
    return f"Report generated!", Path(paths["docx"]), Path(paths["pdf"])

with gr.Blocks() as demo:
    gr.Markdown("# Multi-Agent Research Report Generator")
    topic_input = gr.Textbox(label="Enter Research Topic")
    status = gr.Textbox(label="Status")
    docx_file = gr.File(label="Download DOCX")
    pdf_file = gr.File(label="Download PDF")
    generate_btn = gr.Button("Generate Report")

    generate_btn.click(generate_report, inputs=topic_input, outputs=[status, docx_file, pdf_file])

demo.launch()
