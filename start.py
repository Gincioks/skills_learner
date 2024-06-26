from voyager import VoyagerBrowser, VoyagerPython


openai_api_key = "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"
groq_api_key = "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"

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
    A Search specifies a search of arXiv's database.

    ```
    arxiv.Search(
    query: str = "",
    id_list: List[str] = [],
    max_results: int | None = None,
    sort_by: SortCriterion = SortCriterion.Relevance,
    sort_order: SortOrder = SortOrder.Descending
    )
    ```
    query: an arXiv query string. Advanced query formats are documented in the arXiv API User Manual.
    id_list: list of arXiv record IDs (typically of the format "0710.5765v1"). See the arXiv API User's Manual for documentation of the interaction between query and id_list.
    max_results: The maximum number of results to be returned in an execution of this search. To fetch every result available, set max_results=None (default); to fetch up to 10 results, set max_results=10. The API's limit is 300,000 results.
    sort_by: The sort criterion for results: relevance, lastUpdatedDate, or submittedDate.
    sort_order: The sort order for results: 'descending' or 'ascending'.
    To fetch arXiv records matching a Search, use (Client).results(search) to get a generator yielding Results.

    Example: fetching results
    Print the titles fo the 10 most recent articles related to the keyword "quantum:"
    ```
    import arxiv

    search = arxiv.Search(
    query = "quantum",
    max_results = 10,
    sort_by = arxiv.SortCriterion.SubmittedDate
    )

    for result in arxiv.Client().results(search):
    print(result.title)
    ```
    Fetch and print the title of the paper with ID "1605.08386v1:"

    ```
    import arxiv

    client = arxiv.Client()
    search = arxiv.Search(id_list=["1605.08386v1"])

    paper = next(arxiv.Client().results(search))
    print(paper.title)
    ```
    Result
    The Result objects yielded by (Client).results() include metadata about each paper and some helper functions for downloading their content.

    The meaning of the underlying raw data is documented in the arXiv API User Manual: Details of Atom Results Returned.

    result.entry_id: A url https://arxiv.org/abs/{id}.
    result.updated: When the result was last updated.
    result.published: When the result was originally published.
    result.title: The title of the result.
    result.authors: The result's authors, as arxiv.Authors.
    result.summary: The result abstract.
    result.comment: The authors' comment if present.
    result.journal_ref: A journal reference if present.
    result.doi: A URL for the resolved DOI to an external resource if present.
    result.primary_category: The result's primary arXiv category. See arXiv: Category Taxonomy.
    result.categories: All of the result's categories. See arXiv: Category Taxonomy.
    result.links: Up to three URLs associated with this result, as arxiv.Links.
    result.pdf_url: A URL for the result's PDF if present. Note: this URL also appears among result.links.
    They also expose helper methods for downloading papers: (Result).download_pdf() and (Result).download_source().

    Example: downloading papers
    To download a PDF of the paper with ID "1605.08386v1," run a Search and then use (Result).download_pdf():

    ```
    import arxiv

    paper = next(arxiv.Client().results(arxiv.Search(id_list=["1605.08386v1"])))
    # Download the PDF to the PWD with a default filename.
    paper.download_pdf()
    # Download the PDF to the PWD with a custom filename.
    paper.download_pdf(filename="downloaded-paper.pdf")
    # Download the PDF to a specified directory with a custom filename.
    paper.download_pdf(dirpath="./mydir", filename="downloaded-paper.pdf")
    ```
    The same interface is available for downloading .tar.gz files of the paper source:
    ```
    import arxiv

    paper = next(arxiv.Client().results(arxiv.Search(id_list=["1605.08386v1"])))
    # Download the archive to the PWD with a default filename.
    paper.download_source()
    # Download the archive to the PWD with a custom filename.
    paper.download_source(filename="downloaded-paper.tar.gz")
    # Download the archive to a specified directory with a custom filename.
    paper.download_source(dirpath="./mydir", filename="downloaded-paper.tar.gz")
    ```
    Client
    A Client specifies a strategy for fetching results from arXiv's API; it obscures pagination and retry logic. For most use cases the default client should suffice.
    ```
    # Default client properties.
    arxiv.Client(
    page_size: int = 100,
    delay_seconds: float = 3.0,
    num_retries: int = 3
    )
    ```
    page_size: the number of papers to fetch from arXiv per page of results. Smaller pages can be retrieved faster, but may require more round-trips. The API's limit is 2000 results.
    delay_seconds: the number of seconds to wait between requests for pages. arXiv's Terms of Use ask that you "make no more than one request every three seconds."
    num_retries: The number of times the client will retry a request that fails, either with a non-200 HTTP status code or with an unexpected number of results given the search parameters.
    Example: fetching results with a custom client
    ```
    import arxiv

    big_slow_client = arxiv.Client(
    page_size = 1000,
    delay_seconds = 10.0,
    num_retries = 5
    )

    # Prints 1000 titles before needing to make another request.
    for result in big_slow_client.results(arxiv.Search(query="quantum")):
    print(result.title)
    ```
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
#     system_template = "<|im_start|>system\n{system_message}\n<|im_end|>\n"
#     default_system_message = """I carefully provide accurate, factual, thoughtful, nuanced answers and am brilliant at reasoning.
# I am an assistant who thinks through their answers step-by-step to be sure I always get the right answer.
# I think more clearly if I write out my thought process in a scratchpad manner first; therefore, I always explain background context, assumptions, and step-by-step thinking BEFORE trying to answer or solve anything."""
#     _system_message = _get_system_message(messages)
#     _system_message = (
#         _system_message if _system_message != "" else default_system_message
#     )
#     system_message = system_template.format(system_message=_system_message)

#     _roles = dict(user="<|im_start|>user\n",
#                   assistant="<|im_start|>assistant\n")
#     _sep = "<|im_end|>\n"
#     _stop_str = ["<|im_end|>"]
#     _messages = _map_roles(messages, _roles)
#     _messages.append((_roles["assistant"], None))
#     _prompt = _format_no_colon_single(system_message, _messages, _sep)
#     print(_prompt)
#     return ChatFormatterResponse(prompt=_prompt, stop=_stop_str)
