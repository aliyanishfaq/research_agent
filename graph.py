from typing import TypedDict, List, Dict, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from nodes import understand_query, serp_queries, search_results, draft_report, final_report, is_clarification_needed, scrape_urls
from schema import ResearchState




graph = StateGraph(ResearchState)

graph.add_node("understand", understand_query)
graph.add_node("generate_queries", serp_queries)
graph.add_node("search", search_results)
graph.add_node("synthesize_content", scrape_urls)
graph.add_node("create_draft", draft_report)
graph.add_node("finalize_report", final_report)

# Set entry point
graph.set_entry_point("understand")

# Add edges
graph.add_edge("generate_queries", "search")
graph.add_edge("search", "synthesize_content")
graph.add_edge("synthesize_content", "create_draft")
graph.add_edge("create_draft", "finalize_report")
graph.add_edge("finalize_report", END)

graph.add_conditional_edges(
    "understand",
    is_clarification_needed,
    {
        True: END,
        False: "generate_queries"
    }
)


app = graph.compile()

img = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(img)


# graph.print_graph()







