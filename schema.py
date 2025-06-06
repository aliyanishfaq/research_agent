from pydantic import BaseModel
from typing import List, Dict, TypedDict
from langchain_core.messages import BaseMessage

class ClarificationRequired(BaseModel):
    is_clarification_needed: bool
    question: str

class SearchQueries(BaseModel):
    search_queries: List[str]

class ResearchState(TypedDict):
    messages: List[BaseMessage]
    user_query: str
    clarification_questions: List[str]
    clarification_answers: List[str]
    search_queries: List[str]
    search_urls: Dict[str, List[str]]
    query_content: Dict[str, str]
    draft_report: str
    final_report: str
    is_clarification_needed: bool = False

class PageSummary(BaseModel):
    summary: str