# app.py
import gradio as gr
from src.orchestrator.langgraph_workflow import run_workflow
from pathlib import Path


def generate_report(topic: str):
    if not topic or not topic.strip():
        return "Error: please provide a research topic.", None, None
    paths = run_workflow(topic.strip())
    if isinstance(paths, dict) and "error" in paths:
        return f"Error occurred: {paths['error']}", None, None
    # Expect dict with 'docx' and 'pdf'
    try:
        docx_path = paths.get("docx")
        pdf_path = paths.get("pdf")
        
        # Verify files exist
        if docx_path and not Path(docx_path).exists():
            return "Error: DOCX file was not created.", None, None
            
        return "Report generated successfully!", str(docx_path) if docx_path else None, str(pdf_path) if pdf_path else None
    except Exception as e:
        return f"Error parsing output: {e}", None, None


if __name__ == "__main__":
    with gr.Blocks(title="Research Agent") as demo:
        gr.Markdown("# Multi-Agent Research Report Generator")
        gr.Markdown("Enter a topic below to let the AI agents research, analyze, and write a report for you.")
        
        with gr.Row():
            topic_input = gr.Textbox(label="Enter Research Topic",
                                    value="Climate change impacts on Ethiopian Agriculture",
                                    placeholder="e.g. AI in Healthcare")
        
        generate_btn = gr.Button("Generate Report", variant="primary")
        status = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            docx_file = gr.File(label="Download DOCX")
            pdf_file = gr.File(label="Download PDF")

        generate_btn.click(generate_report, inputs=topic_input,
                        outputs=[status, docx_file, pdf_file])

    try:
        demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True)
    except Exception as e:
        print(f"Failed to launch Gradio app: {e}")
