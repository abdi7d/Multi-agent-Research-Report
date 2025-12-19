import os
import sys
from src.orchestrator.langgraph_workflow import run_workflow

def test_workflow():
    print("Starting test workflow...")
    topic = "The Future of Quantum Computing in 2025"
    print(f"Topic: {topic}")
    
    try:
        result = run_workflow(topic)
        print("\nWorkflow Result:")
        print(result)
        
        if "error" in result:
            print("FAILED: Workflow returned error.")
            sys.exit(1)
            
        docx = result.get("docx")
        pdf = result.get("pdf")
        
        if docx and os.path.exists(docx):
            print(f"SUCCESS: DOCX generated at {docx}")
        else:
            print("FAILED: DOCX invalid.")
            
        if pdf and os.path.exists(pdf):
            print(f"SUCCESS: PDF generated at {pdf}")
        else:
            print("FAILED: PDF invalid.")
            
    except Exception as e:
        print(f"FAILED: Exception during workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure output dir exists
    os.makedirs("outputs", exist_ok=True)
    test_workflow()
