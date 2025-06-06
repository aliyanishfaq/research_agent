CLARIFICATION_REQUIRED_PROMPT = """
 You are part of deep research agent system and you are responsible for understanding the user's query and 
 generating clarification questions if needed.
 The goal with asking clarification questions is to help narrow down the scope of the research
 and make sure the research is comprehensive and relevant.
    
    {context}
    
    Consider:
    1. Is the scope clear enough for comprehensive research?
    2. Are there ambiguous terms that could mean different things?
    3. Is the time frame specified if relevant?
    4. Is the geographic scope clear if relevant?
    5. Is the depth/level of detail clear?
    
    If clarification is needed, generate a specific question that would help clarify the research scope.
    If no clarification is needed, set the value of the "is_clarification_needed" key to False and the "question" key to an empty string.
    
    Format your response in a JSON object with the following keys:
    {{
        "is_clarification_needed": [true/false],
        "question": "[question]"
    }}
    
    Be selective - only ask for clarification if truly necessary for producing a good research report.
    We've already asked {num_questions} clarification questions.
"""

SEARCH_QUERY_GENERATION_PROMPT = """You are a research assistant tasked with generating comprehensive search queries for web research.

Given the user's research query, generate {num_queries} diverse and specific search queries that will help gather comprehensive information on the topic.

User's Research Query: {user_query}

Follow up questions asked from the user:
{clarification_context}

Guidelines for generating search queries:
1. Create queries that cover different aspects of the topic
2. Include both broad overview queries and specific detail queries
3. Use different phrasings and keywords to maximize coverage
4. Include queries for recent developments if relevant
5. Consider different perspectives (technical, practical, historical, current)
6. Use search operators when beneficial (e.g., quotes for exact phrases)
7. Include queries that might find contrasting viewpoints or critiques

Generate exactly {num_queries} search queries that will provide comprehensive coverage of this research topic.

Format your response in a JSON object with the following keys:
{{
    "search_queries": ["[query1]", "[query2]", "[query3]"]
}}
"""

PAGE_CONTENT_SUMMARY_PROMPT = """
You are a research assistant tasked with summarizing the content of a web page.

You need to keep in mind that summary should include details that are relevant to the user's research query.

User's Research Query: {user_query}

Follow up questions asked from the user:
{clarification_context}

Given the content of a web page, generate a very detailed summary of the relevant information.

Page Content: {page_content}

Format your response in a JSON object with the following keys:
{{
    "summary": "summary"
}}
"""