# now combine them all together and state memory also where all agent work together this kins things perform in pipeline
# now create pipeline combine agents all together 1 agent , state , 2 a, search tool 



# 1st import all agent created 

from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dict:  # topic user pass

    state = {}  # state memory as dict because state memory is temp once agent executed memory created later can add db also for permanent 
                # so every stat save some data 
    #search agent working 
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content  # first agent return save in state memory , key created search result 

    print("\n search result ",state['search_results'])


    # 2nd agent connected with state

    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "   # give prompt 
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"  # from url get 1st agent by tavily stored in state 2nd agent read from state
        )]                                                       # search result key give here means first agent content 
    })

    state['scraped_content'] = reader_result['messages'][-1].content  # then perfrom scrap operation and result save in state

    print("\nscraped content: \n", state['scraped_content'])    # create another key scrapped content inside state and save content 
                                                                #  inside it then print that content 



  #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)  # for logs 

    research_combined = (  # create var has two info search_results,scraped_content
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"   # because sorce also give url as reference 
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({ # prepare draft save in state memory for critic chain review
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])



 #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']  # giving report 
    })

    print("\n critic report \n", state['feedback'])

    return state