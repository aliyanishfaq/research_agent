from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from prompts import CLARIFICATION_REQUIRED_PROMPT, SEARCH_QUERY_GENERATION_PROMPT, PAGE_CONTENT_SUMMARY_PROMPT, DEEP_RESEARCH_REPORT_PROMPT
from schema import ClarificationRequired, SearchQueries, ResearchState, PageSummary
from langchain_community.utilities import SerpAPIWrapper
from firecrawl import FirecrawlApp
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from helpers import clarification_context
import os


load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY")

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")


openai_llm = ChatOpenAI(model="gpt-4.1", temperature=0)
firecrawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
openai_reasoning_llm = ChatOpenAI(model="o1")



def understand_query(state: ResearchState) -> ResearchState:
    """
    Understand the user's query and generate clarification questions
    """
    messages = state.get("messages", [])
    user_query = state.get("user_query")
        
    return check_for_clarification(state)

def check_for_clarification(state: ResearchState) -> ResearchState:
    """
    Check if the user's query needs clarification
    """

    clarification_questions = state.get("clarification_questions", [])
    if len(clarification_questions) > 2:
        state["is_clarification_needed"] = False
        return state

    user_query = state.get("user_query")
    clarification_questions = state.get("clarification_questions", [])
    clarification_answers = state.get("clarification_answers", [])

    context = f"User's original research query: {user_query}\n"
    if len(clarification_questions) > 0:
        context += f"Follow up questions asked previously from the user: {clarification_context(clarification_questions, clarification_answers)}\n"
    
    analysis_prompt = CLARIFICATION_REQUIRED_PROMPT.format(context=context, num_questions=len(clarification_questions))
    openai_llm_structured = openai_llm.with_structured_output(ClarificationRequired)
    response = openai_llm_structured.invoke(analysis_prompt)

    state["is_clarification_needed"] = response.is_clarification_needed
    if response.is_clarification_needed:
        state["clarification_questions"].append(response.question)

    return state

def is_clarification_needed(state: ResearchState) -> bool:
    """
    Check if the user's query needs clarification
    """
    return state.get("is_clarification_needed", False)




def serp_queries(state: ResearchState) -> ResearchState:
    """
    Generate search queries based on the user's query
    """
    user_query = state.get("user_query")
    clarification_questions = state.get("clarification_questions", [])
    clarification_answers = state.get("clarification_answers", [])
    num_queries = state.get("breadth", 4)

    clarification = clarification_context(clarification_questions, clarification_answers)

    search_query_prompt = SEARCH_QUERY_GENERATION_PROMPT.format(user_query=user_query, num_queries=num_queries, clarification_context=clarification)
    openai_llm_structured = openai_llm.with_structured_output(SearchQueries)
    response = openai_llm_structured.invoke(search_query_prompt)
    state["search_queries"] = response.search_queries or []
    return state

def search_results(state: ResearchState) -> ResearchState:
    """
    Get search results from the search engine
    """
    search_queries = state.get("search_queries", [])
    num_results = state.get("depth", 3)
    query_map = {}
    web_searcher = SerpAPIWrapper(params={"num": num_results, "gl": "us", "hl": "en"})

    for query in search_queries:
        search_results = web_searcher.results(query)
        search_results = search_results
        if 'organic_results' not in search_results:
            query_map[query] = []
        else:
            query_map[query] = [search_result['link'] for search_result in search_results['organic_results']]

    state["search_urls"] = query_map

    return state

def scrape_urls(state: ResearchState) -> ResearchState:
    """
    Scrape the content from the search results
    """
    search_urls = state.get("search_urls", {})


    for query, urls in search_urls.items():
        relevant_content = ""
        for url in urls:
            print(f"Reading from url: {url}")
            try:
                response = firecrawl_app.scrape_url(url, formats=["markdown", "html"])

            except Exception as e:

                continue

            context = clarification_context(state.get("clarification_questions", []), state.get("clarification_answers", []))
            
            page_summary_prompt = PAGE_CONTENT_SUMMARY_PROMPT.format(user_query=state.get("user_query"), 
                                                                     clarification_context=context, 
                                                                     page_content=response.markdown)
            openai_llm_structured = openai_llm.with_structured_output(PageSummary)
            response = openai_llm_structured.invoke(page_summary_prompt)

            content = f"""
            --------------------------------
            PAGE URL: {url}
            PAGE CONTENT: {response.summary}
            --------------------------------
            """
            relevant_content += content

        state["query_content"][query] = relevant_content

    return state


def draft_report(state: ResearchState) -> ResearchState:
    """
    Generate a draft report based on the search results
    """
    query_content = state.get("query_content", {})
    web_search_results = "Web Search Results:\n"
    for query, content in query_content.items():
        if content:
            web_search_results += f"Query: {query}\n"
            web_search_results += f"Content: {content}\n"
            web_search_results += "--------------------------------\n"

    clarification = clarification_context(state.get("clarification_questions", []), state.get("clarification_answers", []))
    deep_research_report_prompt = DEEP_RESEARCH_REPORT_PROMPT.format(search_results_content=web_search_results, user_query=state.get("user_query"), clarification_context=clarification)
    response = openai_reasoning_llm.invoke(deep_research_report_prompt)
    print(f"Deep Research Report generated")
    state["draft_report"] = response.content
    state["messages"].append(AIMessage(content=response.content))
    return state

def final_report(state: ResearchState) -> ResearchState:
    """
    Generate a final report based on the draft report
    """
    draft_report = state.get("draft_report", "")
    with open("final_report.txt", "w") as f:
        f.write(draft_report)
    state["final_report"] = draft_report
    return state