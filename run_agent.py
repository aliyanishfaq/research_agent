import asyncio
from typing import List, Dict
from langchain_core.messages import HumanMessage
from graph import app

import os
from dotenv import load_dotenv
load_dotenv()


async def run_research():
    """
    Runs the research agent with the user input
    """

    initial_research_question = input("What would you like to research?\n")
    breadth = int(input("How wide should the research be? (3-8)\n"))
    depth = int(input("How narrow should the focus on topics be? (4-6)\n"))

    breadth =  max(3, min(breadth, 8))
    depth =  max(4, min(depth, 6))


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

        if state.get("is_clarification_needed") and len(state.get("clarification_questions")) > len(state.get("clarification_answers")):
            question = state.get("clarification_questions")[-1]
            print(f"Follow Up Question: {question}")
            answer = input("Answer: ")
            state["clarification_answers"].append(answer)
        

if __name__ == "__main__":
    asyncio.run(run_research())
