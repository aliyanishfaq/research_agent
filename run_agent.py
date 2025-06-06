import asyncio
from typing import List, Dict
from langchain_core.messages import HumanMessage
from graph import app

async def run_research():
    """
    Runs the research agent with the user input
    """

    initial_research_question = input("What would you like to research?\n")

    state = {
        "messages": [HumanMessage(content=initial_research_question)],
        "user_query": initial_research_question,
        "clarification_questions": [],
        "clarification_answers": [],
        "search_queries": [],
        "search_urls": {},
        "query_content": {},
        "draft_report": "",
        "final_report": "",
        "is_clarification_needed": False
    }

    while not state.get("final_report"):
        state = await app.ainvoke(state)

        if state.get("is_clarification_needed") and state.get("clarification_questions"):
            question = state.get("clarification_questions")[-1]
            print(f"Follow Up Question: {question}")
            answer = input("Answer: ")
            state["clarification_answers"].append(answer)
        
        break


    print(f"Final Report: {state.get('final_report')}")

if __name__ == "__main__":
    asyncio.run(run_research())
