import re
import time
from typing import List, Union, Dict, Any
from voyager.code_interpreter.control_primitives_context import load_control_primitives_context
from voyager.code_interpreter.prompts import load_prompt

from voyager.types import PythonEvent, ProposedProgram
import voyager.utils as U
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import ast


class ActionAgent:
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0,
        request_timout: int = 120,
        ckpt_dir: str = "ckpt",
        resume: bool = False,
        chat_log: bool = True,
        execution_error: bool = True,
    ):
        self.ckpt_dir = ckpt_dir
        self.chat_log = chat_log
        self.execution_error = execution_error
        U.f_mkdir(f"{ckpt_dir}/action")

        # TODO - resume with workspace?
        # if resume:
        #     print(f"\033[32mLoading Action Agent from {ckpt_dir}/action\033[0m")
        #     self.chest_memory = U.load_json(f"{ckpt_dir}/action/chest_memory.json")
        # else:
        #     self.chest_memory = {}

        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timout,
        )

    def render_system_message(self, skills=[]):
        system_template = load_prompt("action_template")

        if not isinstance(system_template, str):
            raise ValueError("system_template must be a string")

        # FIXME: Hardcoded control_primitives
        base_skills = [
            "writeFile",
            "readFile",
        ]
        programs = "\n\n".join(
            load_control_primitives_context(base_skills) + skills)
        response_format = load_prompt("action_response_format")
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        )
        system_message = system_message_prompt.format(
            programs=programs, response_format=response_format
        )
        assert isinstance(system_message, SystemMessage)
        return system_message

    def render_human_message(
        self, *, events: List[PythonEvent], code="", task="", context="", critique=""
    ):
        chat_messages = []
        error_messages = []

        currentDir = None
        workspace = None
        output = None

        if not events[-1]["log"] == "observe":
            raise ValueError("Last event must be observe")

        for i, (event) in enumerate(events):
            if event["log"] == "observe":
                currentDir = event["currentDir"]
                workspace = event["workspace"]
                output = event["output"]
            elif event["log"] == "error":
                error_messages.append(event["error"])
            else:
                chat_messages.append(event["log"])

        if not currentDir or not workspace or not output:
            raise ValueError("Missing information in events")

        observation = ""

        if code:
            observation += f"Code from the last round:\n{code}\n\n"
        else:
            observation += f"Code from the last round: No code in the first round\n\n"

        if self.execution_error:
            if error_messages:
                # error = "\n".join(error_messages)
                observation += f"Execution error:\n{error_messages}\n\n"
            else:
                observation += f"Execution error: No error\n\n"

        if self.chat_log:
            if chat_messages:
                chat_log = "\n".join(chat_messages)
                observation += f"Chat log: {chat_log}\n\n"
            else:
                observation += f"Chat log: None\n\n"

        observation += f"Current Dir: {currentDir}\n\n"

        observation += f"Workspace: {', '.join(workspace)}\n\n"

        observation += f"Output: {output}\n\n"

        observation += f"Task: {task}\n\n"

        if context:
            observation += f"Context: {context}\n\n"
        else:
            observation += f"Context: None\n\n"

        if critique:
            observation += f"Critique: {critique}\n\n"
        else:
            observation += f"Critique: None\n\n"

        return HumanMessage(content=observation)

    def process_ai_message(self, message) -> Union[ProposedProgram, Exception, str]:
        assert isinstance(message, AIMessage)

        retry = 3
        error = None
        while retry > 0:
            try:
                code_pattern = re.compile(
                    r"```(?:python|py)(.*?)```", re.DOTALL)
                code = "\n".join(code_pattern.findall(message.content))
                # parsed = ast.parse(code)
                # functions: List[Dict[str, Any]] = []
                # assert len(parsed.body) > 0, "No functions found"

                # for node in parsed.body:
                #     if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                #         continue

                #     node_type = (
                #         "AsyncFunctionDef" if isinstance(
                #             node, ast.AsyncFunctionDef) else "FunctionDef"
                #     )

                #     functions.append({
                #         "name": node.name,
                #         "type": node_type,
                #         "body": ast.dump(node),
                #         "params": [arg.arg for arg in node.args.args]
                #     })

                # main_function = None
                # for function in reversed(functions):
                #     if function["name"] == "main":
                #         print(function["name"], "function name")
                #         print(function["type"], "function type")
                #         main_function = function
                #     break

                # if not main_function:
                #     raise Exception(
                #         "No function found. Your main function must be defined.")

                return {
                    "program_code": code,
                    # "program_name": main_function["name"],
                }

            except Exception as e:
                retry -= 1
                error = e
                time.sleep(1)

        return f"Error parsing action response (before program execution): {error}"

    def ensure_main_function_execution(self, code: str, main_function_name: str, is_async: bool) -> str:
        # Pattern to match the execution of the main_function_name
        pattern = re.compile(
            f'{re.escape(main_function_name)}\s*\(\s*\)', re.MULTILINE)

        # Search for the pattern in the code
        if not pattern.search(code):
            # If the pattern is not found, append the execution line to the code
            if is_async:
                code += f'\nasyncio.run({main_function_name}())'
            else:
                code += f'\n{main_function_name}()'

        return code
    # def summarize_chatlog(self, events):
    #     def filter_item(message: str):
    #         craft_pattern = r"I cannot make \w+ because I need: (.*)"
    #         craft_pattern2 = (
    #             r"I cannot make \w+ because there is no crafting table nearby"
    #         )
    #         mine_pattern = r"I need at least a (.*) to mine \w+!"
    #         if re.match(craft_pattern, message):
    #             return re.match(craft_pattern, message).groups()[0]
    #         elif re.match(craft_pattern2, message):
    #             return "a nearby crafting table"
    #         elif re.match(mine_pattern, message):
    #             return re.match(mine_pattern, message).groups()[0]
    #         else:
    #             return ""

    #     chatlog = set()
    #     for event_type, event in events:
    #         if event_type == "onChat":
    #             item = filter_item(event["onChat"])
    #             if item:
    #                 chatlog.add(item)
    #     return "I also need " + ", ".join(chatlog) + "." if chatlog else ""
