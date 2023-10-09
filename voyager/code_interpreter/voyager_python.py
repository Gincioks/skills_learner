import copy
import os
import time
from typing import Dict, Union, List
from langchain.schema import (
    BaseMessage
)
from voyager.types import PythonEvent

import voyager.utils as U
from .env import VoyagerEnvPython

from .agents import ActionAgent
from .agents import CriticAgent
from .agents import CurriculumAgent
from .agents import SkillManager

Conversation = tuple[str, str, str]
Conversations = List[Conversation]
Messages = List[BaseMessage]


class VoyagerPython:
    def __init__(
        self,
        server_port: int = 3001,
        openai_api_key: str or None = "None",
        max_iterations: int = 10,
        env_request_timeout: int = 600,
        reset_placed_if_failed: bool = False,
        action_agent_model_name: str = "gpt-4",
        action_agent_temperature: float = 0,
        action_agent_task_max_retries: int = 4,
        action_agent_show_chat_log: bool = True,
        action_agent_show_execution_error: bool = True,
        curriculum_agent_model_name: str = "gpt-4",
        curriculum_agent_temperature: float = 0,
        curriculum_agent_qa_model_name: str = "gpt-4",
        curriculum_agent_qa_temperature: float = 0,
        curriculum_agent_mode: str = "auto",
        critic_agent_model_name: str = "gpt-4",
        critic_agent_temperature: float = 0,
        critic_agent_mode: str = "auto",
        skill_manager_model_name: str = "gpt-4",
        skill_manager_temperature: float = 0,
        skill_manager_retrieval_top_k: int = 5,
        openai_api_request_timeout: int = 240,
        ckpt_dir: str = "ckpt",
        skill_library_dir: str = "./skill_library",
        resume: bool = False,
    ):
        """
        The main class for Voyager.
        Action agent is the iterative prompting mechanism in paper.
        Curriculum agent is the automatic curriculum in paper.
        Critic agent is the self-verification in paper.
        Skill manager is the skill library in paper.
        """
        # init env
        self.env = VoyagerEnvPython(
            server_port=server_port,
            request_timeout=env_request_timeout,
        )
        self.reset_placed_if_failed = reset_placed_if_failed
        self.max_iterations = max_iterations

        # set openai api key
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # init agents
        self.action_agent = ActionAgent(
            model_name=action_agent_model_name,
            temperature=action_agent_temperature,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            chat_log=action_agent_show_chat_log,
            execution_error=action_agent_show_execution_error,
        )
        self.action_agent_task_max_retries = action_agent_task_max_retries
        self.curriculum_agent = CurriculumAgent(
            model_name=curriculum_agent_model_name,
            temperature=curriculum_agent_temperature,
            qa_model_name=curriculum_agent_qa_model_name,
            qa_temperature=curriculum_agent_qa_temperature,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            mode=curriculum_agent_mode,
        )
        self.critic_agent = CriticAgent(
            model_name=critic_agent_model_name,
            temperature=critic_agent_temperature,
            request_timout=openai_api_request_timeout,
            mode=critic_agent_mode,
        )
        self.skill_manager = SkillManager(
            model_name=skill_manager_model_name,
            temperature=skill_manager_temperature,
            retrieval_top_k=skill_manager_retrieval_top_k,
            request_timout=openai_api_request_timeout,
            ckpt_dir=skill_library_dir if skill_library_dir else ckpt_dir,
            resume=True if resume else False,
        )
        self.recorder = U.EventRecorder(ckpt_dir=ckpt_dir, resume=resume)
        self.resume = resume

        self.action_agent_rollout_num_iter = -1
        self.task = None
        self.context = ""
        self.messages: Messages = []
        self.conversations: Conversations = []
        self.last_events: List[PythonEvent] = []

    def reset(self, task, context="", reset_env=True):
        self.action_agent_rollout_num_iter = 0
        self.task = task
        self.context = context
        if reset_env:
            self.env.reset()

        events = self.env.step("")
        skills = self.skill_manager.retrieve_skills(query=self.context)
        print(
            f"\033[33mRender Action Agent system message with {len(skills)} skills\033[0m"
        )
        system_message = self.action_agent.render_system_message(skills=skills)
        human_message = self.action_agent.render_human_message(
            events=events, code="", task=self.task, context=context, critique=""
        )
        self.messages = [system_message, human_message]
        print(
            f"\033[32m****Action Agent human message****\n{human_message.content}\033[0m"
        )
        assert len(self.messages) == 2
        self.conversations = []
        return self.messages

    def close(self):
        self.env.close()

    def step(self):
        if self.action_agent_rollout_num_iter < 0:
            raise ValueError("Agent must be reset before stepping")
        ai_message = self.action_agent.llm(self.messages)
        print(
            f"\033[34m****Action Agent ai message****\n{ai_message.content}\033[0m")
        self.conversations.append(
            (self.messages[0].content,
             self.messages[1].content, ai_message.content)
        )
        parsed_result = self.action_agent.process_ai_message(
            message=ai_message)
        success = False

        if self.task is None:
            raise ValueError("Task must be set before stepping")

        if isinstance(parsed_result, dict):
            code = parsed_result["program_code"] + \
                "\n" + parsed_result["exec_code"]
            events = self.env.step(
                imports=parsed_result["imports"],
                code=code,
                programs=self.skill_manager.programs,
            )
            self.recorder.record(events, self.task)
            success, critique = self.critic_agent.check_task_success(
                events=events,
                task=self.task,
                context=self.context,
                max_retries=5,
            )

            print(f"\033[34m{success}\033[0m", "success")

            new_skills = self.skill_manager.retrieve_skills(
                query=self.context
            )
            system_message = self.action_agent.render_system_message(
                skills=new_skills)

            human_message = self.action_agent.render_human_message(
                events=events,
                code=parsed_result["program_code"],
                task=self.task,
                context=self.context,
                critique=critique,
            )
            self.last_events = copy.deepcopy(events)
            self.messages = [system_message, human_message]
        else:
            assert isinstance(parsed_result, str)
            self.recorder.record([], self.task)
            print(f"\033[34m{parsed_result} Trying again!\033[0m")
        assert len(self.messages) == 2
        self.action_agent_rollout_num_iter += 1
        done = (
            self.action_agent_rollout_num_iter >= self.action_agent_task_max_retries
            or success
        )
        info: Dict[str, Union[str, bool, Conversations]] = {
            "task": self.task,
            "success": success,
            "conversations": self.conversations,
        }
        if success:

            if not isinstance(parsed_result, dict):
                raise ValueError(
                    f"parsed_result must be a proposed program on success, got {type(parsed_result)}"
                )

            info["program_code"] = parsed_result["program_code"]
            info["program_name"] = parsed_result["program_name"]

        else:
            print(
                f"\033[32m****Action Agent human message****\n{self.messages[-1].content}\033[0m"
            )
        return self.messages, 0, done, info

    def rollout(self, *, task, context, reset_env=True):
        self.reset(task=task, context=context, reset_env=reset_env)
        while True:
            messages, reward, done, info = self.step()
            if done:
                break
        return messages, reward, done, info

    def learn(self, init_task: str, init_context: str, reset_env=True):
        self.env.reset()
        self.last_events = self.env.step("")
        while True:
            if self.recorder.iteration > self.max_iterations:
                print("Iteration limit reached")
                break
            task, context = self.curriculum_agent.propose_next_task(
                events=self.last_events,
                max_retries=5,
                task=init_task,
                context=init_context,
            )
            print(
                f"\033[35mStarting task {task} for at most {self.action_agent_task_max_retries} times\033[0m"
            )
            try:
                messages, reward, done, info = self.rollout(
                    task=task,
                    context=context,
                    reset_env=reset_env,
                )
            except Exception as e:
                time.sleep(3)
                info = {
                    "task": task,
                    "success": False,
                }

                last_event = self.last_events[-1]
                if not isinstance(last_event, dict):
                    raise ValueError(f"There must be browser events present")

                self.env.reset(
                    options={
                        "workspace": last_event["workspace"],
                        "currentDir": last_event["currentDir"],
                        "output": last_event["output"],
                    }
                )

                print("Your last round rollout terminated due to error:")
                print(f"\033[41m{e}\033[0m")

            if info["success"]:
                self.skill_manager.add_new_skill(info)

            self.curriculum_agent.update_exploration_progress(info)
            print(
                f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
            )
            print(
                f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            )

        return {
            "completed_tasks": self.curriculum_agent.completed_tasks,
            "failed_tasks": self.curriculum_agent.failed_tasks,
            "skills": self.skill_manager.skills,
        }

    def decompose_task(self, task):
        # if not self.last_events:
        #     self.last_events = self.env.reset(
        #         options={
        #             "mode": "hard",
        #             "wait_ticks": self.env_wait_ticks,
        #         }
        #     )
        # return self.curriculum_agent.decompose_task(task, self.last_events)
        print("Not implemented - task decomposition")

    def inference(self, task=None, sub_goals=[], reset_mode="hard", reset_env=True):
        # if not task and not sub_goals:
        #     raise ValueError("Either task or sub_goals must be provided")
        # if not sub_goals:
        #     sub_goals = self.decompose_task(task)
        # self.env.reset(
        #     options={
        #         "mode": reset_mode,
        #         "wait_ticks": self.env_wait_ticks,
        #     }
        # )
        # self.curriculum_agent.completed_tasks = []
        # self.curriculum_agent.failed_tasks = []
        # self.last_events = self.env.step("")
        # while self.curriculum_agent.progress < len(sub_goals):
        #     next_task = sub_goals[self.curriculum_agent.progress]
        #     context = self.curriculum_agent.get_task_context(next_task)
        #     print(
        #         f"\033[35mStarting task {next_task} for at most {self.action_agent_task_max_retries} times\033[0m"
        #     )
        #     messages, reward, done, info = self.rollout(
        #         task=next_task,
        #         context=context,
        #         reset_env=reset_env,
        #     )
        #     self.curriculum_agent.update_exploration_progress(info)
        #     print(
        #         f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
        #     )
        #     print(
        #         f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
        #     )
        print("Not implemented - task inference")
