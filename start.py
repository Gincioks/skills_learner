from voyager import Voyager

openai_api_key = "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"

voyager = Voyager(
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()
