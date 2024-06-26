import openai
from langchain.schema import (
    AIMessage
)


class OpenAIChat:
    BASE_SYSTEM_MESSAGE = """I carefully provide accurate, factual, thoughtful, nuanced answers and am brilliant at reasoning. 
    I am an assistant who thinks through their answers step-by-step to be sure I always get the right answer. 
    I think more clearly if I write out my thought process in a scratchpad manner first; therefore, I always explain background context, assumptions, and step-by-step thinking BEFORE trying to answer or solve anything."""

    def __init__(self, api_base=None, api_key=None,
                 max_tokens=4096, temperature=0.4, top_p=0.95, top_k=40, repetition_penalty=1.1):
        if api_base:
            openai.api_base = api_base
        if api_key:
            openai.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repetition_penalty = repetition_penalty

    def make_prediction(self, prompt):
        if self.temperature == 0:
            self.top_p = 1
            self.top_k = -1

        completion = openai.Completion.create(
            model="Open-Orca/Mistral-7B-OpenOrca",
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            stream=False,
            stop=["</s>", "<|im_end|>"]
        )
        return completion

    def ask(self, system_message, history, stop=None):
        history = history or []

        messages = self.format_chat_lm(system_message, history)
        prediction = self.make_prediction(messages)

        if prediction["choices"][0]["text"][0] == ":":
            print(prediction["choices"][0]["text"],
                  "kas cia---------------------------")
            return AIMessage(content=prediction["choices"][0]["text"][2:])

        return AIMessage(content=prediction["choices"][0]["text"])

    def format_chat_lm(self, system_message, history):
        if system_message.strip():
            messages = "<|im_start|> "+"system\n" + system_message.strip() + "<|im_end|>\n" + \
                "\n".join(["\n".join(["<|im_start|> "+"user\n"+item[0]+"<|im_end|>", "<|im_start|> assistant\n"+item[1]+"<|im_end|>"])
                           for item in history])
        else:
            messages = "<|im_start|> "+"system\n" + self.BASE_SYSTEM_MESSAGE + "<|im_end|>\n" + \
                "\n".join(["\n".join(["<|im_start|> "+"user\n"+item[0]+"<|im_end|>", "<|im_start|> assistant\n"+item[1]+"<|im_end|>"])
                           for item in history])
        # strip the last `<|end_of_turn|>` from the messages
        messages = messages.rstrip("<|im_end|>")
        # remove last space from assistant, some models output a ZWSP if you leave a space
        messages = messages.rstrip()
        return messages

    def format_xwin_lm(self, system_message, history):
        if system_message.strip():
            messages = system_message.strip() + " " + \
                "".join(["".join(["USER:"+item[0]+" ", "ASSISTANT:"+item[1]+"</s>"])
                         for item in history])
        else:
            messages = self.BASE_SYSTEM_MESSAGE + " " + \
                "".join(["".join(["USER:"+item[0]+" ", "ASSISTANT:"+item[1]+"</s>"])
                         for item in history])
        messages = messages.rstrip("</s>")
        messages = messages.rstrip()
        return messages
