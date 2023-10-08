from voyager import VoyagerBrowser

openai_api_key = "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"

voyager = VoyagerBrowser(
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()
