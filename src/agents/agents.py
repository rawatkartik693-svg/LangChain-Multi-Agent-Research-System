# agent implementation

from langchain.agents import create_agent # previous import create_react_agent because older version og langchain but now this func
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate # prepare custom prompt in 3rd agent
from langchain_core.output_parsers import StrOutputParser # because use lcel modern langchain expression/syntax
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv() #  initilie dot env


# Model Initialization
llm = ChatOpenAI(model="gpt-4o-mini", 
api_key=os.getenv("OPEN_ROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1", temperature=0)



# 1st Agent : Search Agent
def build_search_agent():      # agent creation  search agent 
    return create_agent(
        model= llm,
        tools=[web_search], #  system can be modify
    )                                 


# 2nd Agent : Reader Agent
def build_reader_agent():
    return create_agent(
        model= llm,
        tools=[scrape_url],

    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([ # prepare prompt 
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}  # come from human input and this will take the reserach , 
                # it will get research from reader agent to write agent for write draft

Research Gathered:
{research}

Structure the report as:   # this info need in draft can change according to requirements
- Introduction 
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser() # promt go to llm try to work on that llm expecting 
# topic(user), research (reader agent) reader agent return reserch content wth help of reserach content refer
# and write report not need to create agent lcel can do 




#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()


# now combine them all together and state memory also where all agent work together this kins things perform in pipeline
# now create pipeline combine agents all together 1 agent , state , 2 a, search tool 

