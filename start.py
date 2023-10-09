from voyager import VoyagerBrowser, VoyagerPython


openai_api_key = "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"

# voyager = VoyagerBrowser(
#     openai_api_key=openai_api_key,
# )

voyager = VoyagerPython(
    openai_api_key=openai_api_key,
    critic_agent_mode="auto"
)

# start lifelong learning
voyager.learn(
    init_task="find papers on LLM applications from arxiv in the last week, create a markdown table of different domains and save to file",
    init_context="Use arxiv python packpage"  # noqa: E501"
)
