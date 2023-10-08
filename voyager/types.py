from typing import Dict, List, TypedDict


class FunctionDescription(TypedDict):
    name: str
    type: str
    body: str
    params: List


class ProposedProgram(TypedDict):
    program_code: str
    program_name: str
    exec_code: str


class Clickable(TypedDict):
    id: str
    type: str
    text: str
    attributes: Dict[str, str]


class ResetOptions(TypedDict):
    clickables: Dict[str, Clickable]
    currentUrl: str
    workspace: List[str]
    text: str


class ResetOptionsPython(TypedDict):
    currentDir: str
    workspace: List[str]
    output: str


class BrowserEvent (TypedDict):
    log: str
    workspace: List[str]
    currentUrl: str
    clickables: Dict[str, Clickable]
    error: str
    text: str


class PythonEvent (TypedDict):
    log: str
    workspace: List[str]
    currentDir: str
    error: str
    output: str
