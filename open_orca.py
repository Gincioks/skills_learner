import os
import re
import logging
import gradio as gr
import openai

print(os.environ)
# openai.api_base = os.environ.get("OPENAI_API_BASE")
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "sk-rfggvnkrgvfgv"

BASE_SYSTEM_MESSAGE = """I carefully provide accurate, factual, thoughtful, nuanced answers and am brilliant at reasoning. 
I am an assistant who thinks through their answers step-by-step to be sure I always get the right answer. 
I think more clearly if I write out my thought process in a scratchpad manner first; therefore, I always explain background context, assumptions, and step-by-step thinking BEFORE trying to answer or solve anything."""


def make_prediction(prompt, max_tokens=None, temperature=None, top_p=None, top_k=None, repetition_penalty=None):
    completion = openai.Completion.create(model="Open-Orca/Mistral-7B-OpenOrca", prompt=prompt, max_tokens=max_tokens, temperature=temperature,
                                          top_p=top_p, top_k=top_k, repetition_penalty=repetition_penalty, stream=True, stop=["</s>", "<|im_end|>"])
    for chunk in completion:
        yield chunk["choices"][0]["text"]


def clear_chat(chat_history_state, chat_message):
    chat_history_state = []
    chat_message = ''
    return chat_history_state, chat_message


def user(message, history):
    history = history or []
    # Append the user's message to the conversation history
    history.append([message, ""])
    return "", history


def chat(history, system_message, max_tokens, temperature, top_p, top_k, repetition_penalty):
    history = history or []

    print(history, "history")

    if system_message.strip():
        messages = "<|im_start|> "+"system\n" + system_message.strip() + "<|im_end|>\n" + \
                   "\n".join(["\n".join(["<|im_start|> "+"user\n"+item[0]+"<|im_end|>", "<|im_start|> assistant\n"+item[1]+"<|im_end|>"])
                              for item in history])
    else:
        messages = "<|im_start|> "+"system\n" + BASE_SYSTEM_MESSAGE + "<|im_end|>\n" + \
                   "\n".join(["\n".join(["<|im_start|> "+"user\n"+item[0]+"<|im_end|>", "<|im_start|> assistant\n"+item[1]+"<|im_end|>"])
                              for item in history])
    # strip the last `<|end_of_turn|>` from the messages
    messages = messages.rstrip("<|im_end|>")
    # remove last space from assistant, some models output a ZWSP if you leave a space
    messages = messages.rstrip()

    # If temperature is set to 0, force Top P to 1 and Top K to -1
    if temperature == 0:
        top_p = 1
        top_k = -1

    prediction = make_prediction(
        messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
    )
    for tokens in prediction:
        tokens = re.findall(r'(.*?)(\s|$)', tokens)
        for subtoken in tokens:
            subtoken = "".join(subtoken)
            answer = subtoken
            history[-1][1] += answer
            # stream the response
            yield history, history, ""


start_message = ""

CSS = """
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; overflow: auto; resize: vertical; }
"""

# with gr.Blocks() as demo:
with gr.Blocks(css=CSS) as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown(f"""
                    ## This demo is an unquantized GPU chatbot of [Mistral-7B-OpenOrca](https://huggingface.co/Open-Orca/Mistral-7B-OpenOrca)
                    Brought to you by your friends at Alignment Lab AI, OpenChat, and Open Access AI Collective!
                    """)
    with gr.Row():
        gr.Markdown("# 🐋 Mistral-7B-OpenOrca Playground Space! 🐋")
    with gr.Row():
        # chatbot = gr.Chatbot().style(height=500)
        chatbot = gr.Chatbot(elem_id="chatbot")
    with gr.Row():
        message = gr.Textbox(
            label="What do you want to chat about?",
            placeholder="Ask me anything.",
            lines=3,
        )
    with gr.Row():
        submit = gr.Button(value="Send message",
                           variant="secondary").style(full_width=True)
        clear = gr.Button(value="New topic", variant="secondary").style(
            full_width=False)
        stop = gr.Button(value="Stop", variant="secondary").style(
            full_width=False)
    with gr.Accordion("Show Model Parameters", open=False):
        with gr.Row():
            with gr.Column():
                max_tokens = gr.Slider(
                    20, 2500, label="Max Tokens", step=20, value=500)
                temperature = gr.Slider(
                    0.0, 2.0, label="Temperature", step=0.1, value=0.4)
                top_p = gr.Slider(0.0, 1.0, label="Top P",
                                  step=0.05, value=0.95)
                top_k = gr.Slider(1, 100, label="Top K", step=1, value=40)
                repetition_penalty = gr.Slider(
                    1.0, 2.0, label="Repetition Penalty", step=0.1, value=1.1)

        system_msg = gr.Textbox(
            start_message, label="System Message", interactive=True, visible=True, placeholder="System prompt. Provide instructions which you want the model to remember.", lines=5)

    chat_history_state = gr.State()
    clear.click(clear_chat, inputs=[chat_history_state, message], outputs=[
                chat_history_state, message], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

    submit_click_event = submit.click(
        fn=user, inputs=[message, chat_history_state], outputs=[
            message, chat_history_state], queue=True
    ).then(
        fn=chat, inputs=[chat_history_state, system_msg, max_tokens, temperature, top_p, top_k,
                         repetition_penalty], outputs=[chatbot, chat_history_state, message], queue=True
    )
    stop.click(fn=None, inputs=None, outputs=None,
               cancels=[submit_click_event], queue=False)

demo.queue(max_size=128, concurrency_count=48).launch(
    debug=True, server_name="0.0.0.0", server_port=7860)
