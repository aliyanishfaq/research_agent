from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from prompts import CLARIFICATION_REQUIRED_PROMPT, SEARCH_QUERY_GENERATION_PROMPT, PAGE_CONTENT_SUMMARY_PROMPT
from schema import ClarificationRequired, SearchQueries, ResearchState, PageSummary
from langchain_community.utilities import SerpAPIWrapper
from firecrawl import FirecrawlApp
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os


load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY")


openai_llm = ChatOpenAI(model="gpt-4o", temperature=0)
firecrawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))



def understand_query(state: ResearchState) -> ResearchState:
    """
    Understand the user's query and generate clarification questions
    """
    messages = state.get("messages", [])
    user_query = state.get("user_query")

    return state
        
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
    if clarification_answers:
        for i, (q, a) in enumerate(zip(clarification_questions, clarification_answers)):
            context += f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n"
    
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
    num_queries = state.get("breadth", 3)

    context = "\n"
    if clarification_answers:
        for i, (q, a) in enumerate(zip(clarification_questions, clarification_answers)):
            context += f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n\n"

    search_query_prompt = SEARCH_QUERY_GENERATION_PROMPT.format(user_query=user_query, num_queries=num_queries, clarification_context=context)
    openai_llm_structured = openai_llm.with_structured_output(SearchQueries)
    response = openai_llm_structured.invoke(search_query_prompt)
    print(f"Search queries: {response.search_queries}") 
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

    print(f"Query map: {query_map}")
    state["search_urls"] = query_map

    return state

def scrape_urls(state: ResearchState) -> ResearchState:
    """
    Scrape the content from the search results
    """
    print(f"Scraping urls: {state.get('search_urls')}")
    search_urls = state.get("search_urls", {})


    for query, urls in search_urls.items():
        relevant_content = ""
        for url in urls:
            try:
                response = firecrawl_app.scrape_url(url, formats=["markdown", "html"])

            except Exception as e:
                print(f"Error scraping url: {url}")
                continue
            
            page_summary_prompt = PAGE_CONTENT_SUMMARY_PROMPT.format(user_query=state.get("user_query"), 
                                                                     clarification_context=state.get("clarification_context"), 
                                                                     page_content=response.markdown)
            openai_llm_structured = openai_llm.with_structured_output(PageSummary)
            response = openai_llm_structured.invoke(page_summary_prompt)
            print(f"Response: {response}")
            content = f"""
            --------------------------------
            PAGE URL: {url}
            PAGE CONTENT: {response.summary}
            --------------------------------
            """
            relevant_content += content
        print(f"Relevant content: {relevant_content}")
        state["query_content"][query] = relevant_content

    return state


def draft_report(state: ResearchState) -> ResearchState:
    """
    Generate a draft report based on the search results
    """
    query_content = state.get("query_content", {})
    content = "Web Search Results:\n"
    for query, content in query_content.items():
        if content:
            content += f"Query: {query}\n"
            content += f"Content: {content}\n"
            content += "--------------------------------\n"

    return state


def final_report(state: ResearchState) -> ResearchState:
    """
    Generate a final report based on the draft report
    """
    
    return state