from voyager import VoyagerBrowser, VoyagerPython


openai_api_key = "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"

# voyager = VoyagerBrowser(
#     openai_api_key=openai_api_key,
# )

voyager = VoyagerPython(
    openai_api_key=openai_api_key,
    action_agent_model_name="gpt-4",
    curriculum_agent_model_name="gpt-4",
    curriculum_agent_qa_model_name="gpt-4",
    critic_agent_model_name="gpt-4",
    skill_manager_model_name="gpt-4",
    curriculum_agent_mode="auto",
    critic_agent_mode="auto"
)

# start lifelong learning
voyager.learn(
    init_task="find papers on LLM applications from arxiv in the last week, create a markdown table of different domains and save to file",
    init_context="""
    Hint's:
    - Code executor working in macOS
    - Use requests, datetime and BeautifulSoup
    Goals:
    - find papers on LLM applications from arxiv in the last week
    - create a markdown table of different domains from papers
    - make sure the table is sorted by the number of papers in each domain
    - make sure table is not empty
    - save to file
    """  # noqa: E501"
)
# voyager.learn(
#     init_task="Develop skills for autonomous ai agent.",
#     init_context="You need to be the best skill system for ai agents"  # noqa: E501"
# )
