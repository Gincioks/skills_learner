from typing import List
from voyager.code_interpreter.prompts import load_prompt
from voyager.types import PythonEvent
from voyager.utils.json_utils import fix_and_parse_json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class CriticAgent:
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0,
        request_timout: int = 120,
        mode: str = "auto",
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timout,
            openai_api_base="http://localhost:8000/v1",
            max_tokens=8192,
        )
        assert mode in ["auto", "manual"]
        self.mode = mode

    def render_system_message(self):
        system_message = SystemMessage(content=load_prompt("critic"))
        return system_message

    def render_human_message(self, *, events: List[PythonEvent], task, context):

        if not events[-1]["log"] == "observe":
            raise ValueError("Last event must be an observe event")

        event = events[-1]
        current_dir = event["currentDir"]
        workspace = event["workspace"]
        output = event["output"]
        error = event["error"]

        for i, (event) in enumerate(events):
            if event["log"] == "error":
                print(
                    f"\033[31mCritic Agent: Error occurs {event['error']}\033[0m")
                return None

        observation = ""

        if not current_dir:
            raise ValueError("Missing required fields")

        observation += f"Current Dir: {current_dir}\n\n"

        if workspace:
            observation += f"Workspace: {', '.join(workspace)}\n\n"
        else:
            observation += f"Workspace: None\n\n"

        if error:
            # error = "\n".join(error_messages)
            observation += f"Execution error:\n{error}\n\n"
        else:
            observation += f"Output: {output}\n\n"

        observation += f"Task: {task}\n\n"

        if context:
            observation += f"Context: {context}\n\n"
        else:
            observation += f"Context: None\n\n"

        print(
            f"\033[31m****Critic Agent human message****\n{observation}\033[0m")
        return HumanMessage(content=observation)

    def human_check_task_success(self):
        confirmed = False
        success = False
        critique = ""
        while not confirmed:
            success = input("Success? (y/n)")
            success = success.lower() == "y"
            critique = input("Enter your critique:")
            print(f"Success: {success}\nCritique: {critique}")
            confirmed = input("Confirm? (y/n)") in ["y", ""]
        return success, critique

    def ai_check_task_success(self, messages, max_retries=5):
        if max_retries == 0:
            print(
                "\033[31mFailed to parse Critic Agent response. Consider updating your prompt.\033[0m"
            )
            return False, ""

        if messages[1] is None:
            return False, ""

        critic = self.llm(messages).content
        print(f"\033[31m****Critic Agent ai message****\n{critic}\033[0m")
        try:
            response = fix_and_parse_json(critic)
            assert response["success"] in [True, False]
            if "critique" not in response:
                response["critique"] = ""
            return response["success"], response["critique"]
        except Exception as e:
            print(
                f"\033[31mError parsing critic response: {e} Trying again!\033[0m")
            return self.ai_check_task_success(
                messages=messages,
                max_retries=max_retries - 1,
            )

    def check_task_success(
        self, *, events, task, context, max_retries=5
    ):
        human_message = self.render_human_message(
            events=events,
            task=task,
            context=context,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        if self.mode == "manual":
            return self.human_check_task_success()
        elif self.mode == "auto":
            return self.ai_check_task_success(
                messages=messages, max_retries=max_retries
            )
        else:
            raise ValueError(f"Invalid critic agent mode: {self.mode}")
