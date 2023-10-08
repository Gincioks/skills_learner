from fastapi import FastAPI, Request
import json
import os
from IPython import get_ipython

app = FastAPI()
events_cache = []


def exec_python(cell):
    ipython = get_ipython()
    result = ipython.run_cell(cell)
    log = str(result.result)
    if result.error_before_exec is not None:
        log += f"\n{result.error_before_exec}"
    if result.error_in_exec is not None:
        log += f"\n{result.error_in_exec}"
    return log


def get_current_dir():
    path = os.getcwd()  # Use os.getcwd() to get the current working directory
    return path


def record_event(log, output=None, error=None):
    global events_cache
    workspace = os.listdir(os.path.join(
        os.path.dirname(__file__), "./workspace"))

    event = {
        "log": log,
        "workspace": workspace,
        "currentDir": get_current_dir(),
        "error": error,
        "output": output,
    }
    events_cache.append(event)


@app.post("/execute")
async def execute(request: Request):
    global events_cache
    req_data = await request.json()
    code = req_data.get("code", "").replace(
        "\r\n", "").replace("\n", "").replace("\r", "")
    programs = req_data.get("programs", "").replace(
        "\r\n", "").replace("\n", "").replace("\r", "")

    print(f"Received code: {code}")
    print(f"Received programs: {programs}")

    if not code and not programs:
        print("No code or programs received.")
        record_event("observe", "No code or programs received.")

    try:
        if code and programs:
            combined_code = f"{programs}; {code}"
            print(f"Executing combined code: {combined_code}")
            output = exec_python(combined_code)
            print("Executed code successfully.")
            print("Recorded event.")
            record_event("observe", output)
    except Exception as e:
        print(f"Exception: {e}")
        record_event("error", None, error=str(e))

    with open("./workspace/events.json", "w") as f:
        json.dump(events_cache, f, indent=2)

    response = {"events": events_cache}
    print(response, "kas cia")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
