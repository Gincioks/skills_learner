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
    Notes:
    - Code executor working in macOS
    - Use requests, datetime and BeautifulSoup
    Requirements:
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

# voyager.learn(
#     init_task="Learn use this api https://restaurant-api.wolt.com/v4/venues/slug/stasio-kampas/menu/data?unit_prices=true&show_weighted_items=true&show_subcategories=true",
#     init_context="""
#     Hint's:
#     - Code executor working in macOS
#     - This api from food delivery service
#     Goals:
#     - Use this api https://restaurant-api.wolt.com/v4/venues/slug/stasio-kampas/menu/data?unit_prices=true&show_weighted_items=true&show_subcategories=true
#     - Get all categories
#     - Get all items in categories
#     - Get all items
#     - Get all items in menu
#     - Get all items in menu with price
#     """
# )


# @register_chat_format("mistral-orca")
# def format_mistal_orca(
#     messages: List[llama_types.ChatCompletionRequestMessage],
#     **kwargs: Any,
# ) -> ChatFormatterResponse:
#     system_template = "<|im_start|> system\n {system_message} \n"
#     default_system_message = """I carefully provide accurate, factual, thoughtful, nuanced answers and am brilliant at reasoning.
# I am an assistant who thinks through their answers step-by-step to be sure I always get the right answer.
# I think more clearly if I write out my thought process in a scratchpad manner first; therefore, I always explain background context, assumptions, and step-by-step thinking BEFORE trying to answer or solve anything."""
#     _system_message = _get_system_message(messages)
#     _system_message = (
#         _system_message if _system_message != "" else default_system_message
#     )
#     system_message = system_template.format(system_message=_system_message)

#     _roles = dict(user="<|im_start|> user\n",
#                   assistant="<|im_start|> assistant\n")
#     _sep = "<|im_end|>"
#     _stop_str = ["</s>"]
#     _messages = _map_roles(messages, _roles)
#     _messages.append((_roles["assistant"], None))
#     _prompt = _format_add_colon_single(system_message, _messages, _sep)
#     return ChatFormatterResponse(prompt=_prompt, stop=_stop_str)
