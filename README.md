### High-level design

**Agents**
- ResearchAgent — gathers web content using a Web Search tool or optional SerpAPI; stores raw snippets + metadata.

- AnalysisAgent — ingests research results, de-duplicates, ranks by relevance, extracts outlines, and produces a structured brief.

- ReportWriterAgent — takes the structured brief and produces a formatted report (Markdown/HTML) and exports to PDF or DOCX using a Document Generator Tool.


**Tools**

- WebSearchTool — wrapper around SerpAPI / Bing / Google Custom Search. Optional. If not configured, a demo mock search returns a curated sample set (useful for local dev).

- SummarizationTool — small helper using Google GenAI to summarize long text chunks.

- DocumentGeneratorTool — uses Python libraries (python-docx, weasyprint or reportlab) to generate DOCX and PDF.


**Orchestration**

- LangGraph graph models the workflow: start → research_node → analyze_node → write_node → export_node. LangGraph manages retries, durable state, and transitions.

**Interface**

- Gradio UI: a simple web form to submit topic, options (depth, number of sources), and buttons to run the pipeline and download results.

**LLM**

- Use google-genai Python SDK (Gemini/GenAI). Provide code using the official client pattern and safe “mock” stub for local testin



### Repository Structure 


```

multiagent-research-report/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ start.sh
├─ dockerfile (optional)
├─ app.py                     # Gradio UI + starts orchestration
├─ src/
│  ├─ config.py               # central config loader (env vars)
│  ├─ orchestrator/
│  │  └─ langgraph_workflow.py  # LangGraph graph that wires agents
│  ├─ agents/
│  │  ├─ research_agent.py
│  │  ├─ analysis_agent.py
│  │  └─ report_writer_agent.py
│  ├─ tools/
│  │  ├─ web_search.py         # SerpAPI or mock web search wrapper
│  │  ├─ summarizer.py        # short extraction utilities (LLM + heuristics)
│  │  └─ doc_generator.py     # create DOCX and PDF
│  └─ utils/
│     └─ llm_client.py        # thin wrapper around Google GenAI client
└─ examples/
   └─ sample_report.pdf
```


Ask: Climate change impacts on Ethiopian Agriculture

