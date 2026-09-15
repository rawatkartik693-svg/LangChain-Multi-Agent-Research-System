# test here 
from src.pipelines.pipeline import run_research_pipeline
#from src.tools.tools import web_search,scrape_url

#web_search("latest advancements in AI research") # give 5 statement but not clear enough to give answer to question.
                                                 # need tool rich  helps us  to se  good print statemnt also use logging /debugging


#output=web_search("latest advancements in AI research")
#print(output)

#web_search.invoke("what is the latest research on ai")

topic = "The impact of AI on the job market in 2026"
run_research_pipeline(topic)