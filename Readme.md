# Research Agent 🔬

 Research agent built using LangChain, OpenAI, LangGraph, and LangSmith that automatically conducts comprehensive web research and generates detailed reports.

## Features

- **Intelligent Query Understanding**: Asks clarifying questions to better understand research topics
- **Multi-source Web Search**: Uses SerpAPI to find relevant sources across the web
- **Content Extraction**: Scrapes and processes web content using FireCrawl API
- **AI-Powered Synthesis**: Uses OpenAI's GPT models to analyze and synthesize information
- **Comprehensive Reporting**: Generates detailed research reports in markdown format


## Prerequisites

- Python 3.8 or higher
- API keys for:
  - OpenAI (required)
  - SerpAPI (required)
  - FireCrawl (required)
  - LangSmith (optional - for tracing)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/aliyanishfaq/research-agent.git
cd research-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional: LangSmith Tracing (set to false to disable)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=research-agent
```

**Note**: LangSmith tracing is optional and can be disabled by setting `LANGCHAIN_TRACING_V2=false` or omitting it entirely.

## Usage

### Running the Research Agent

```bash
python run_agent.py
```

### User Inputs

The agent will prompt you for the following information:

1. **Research Query**: What topic you want to research
2. **Breadth** (3-6): How many search queries to generate for broader coverage
3. **Depth** (1-5): How many search results to process per query
4. **Follow-up Questions**: The agent may ask clarifying questions to better understand your research needs

### Example Session

```
What would you like to research?
> Anthropic's Model Context Protocol

How wide should the research be? (3-6, default: 3)
> 4

How narrow should the focus on topics be? (1-5, default: 3)
> 3

[Agent may ask follow-up questions like:]
Follow Up Question: Are you more interested in the technical implementation or business applications?
Answer: > Technical implementation
```

## How It Works

The research agent follows a systematic workflow:

### 1. **Query Understanding**
- Analyzes your research question
- Asks clarifying questions if needed to better understand the scope and focus

### 2. **Search Query Generation**
- Generates multiple targeted search queries based on your input
- Uses AI to create diverse queries that cover different aspects of the topic

### 3. **Web Search** 
- Uses SerpAPI to find relevant URLs from search engines
- Collects multiple sources per query for comprehensive coverage

### 4. **Content Extraction**
- Uses FireCrawl API to scrape and extract clean content from web pages
- Handles various content types and formats automatically

### 5. **Content Synthesis**
- AI analyzes and summarizes content from each source
- Identifies key insights and relevant information related to your query

### 6. **Report Generation**
- Combines all findings into a comprehensive research report
- Uses advanced AI models (including OpenAI's reasoning models) to create structured, insightful reports

### 7. **Output**
- Saves the final report as `final_report.txt`

## Output Files

- `final_report.txt` - The complete research report in markdown format

## Configuration

### Adjusting Research Parameters

You can modify the following parameters in `run_agent.py`:

- **Breadth** (3-6): More breadth = more diverse search queries
- **Depth** (1-5): More depth = more sources per query
- **Models**: Change AI models in `nodes.py` if needed


## API Key Setup Instructions

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key

### SerpAPI Key  
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for an account
3. Get your API key from the dashboard

### FireCrawl API Key
1. Go to [FireCrawl](https://firecrawl.dev/)
2. Sign up for an account  
3. Get your API key from the dashboard

### LangSmith (Optional)
1. Go to [LangSmith](https://smith.langchain.com/)
2. Create an account
3. Get your API key for tracing and monitoring