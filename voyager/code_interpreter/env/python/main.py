from fastapi import FastAPI, Request
import json
import os
import subprocess
import tempfile


app = FastAPI()
events_cache = []


def exec_python(code):
    try:
       # save code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(code)
            temp_file_name = f.name

        # execute code
        result = subprocess.run(
            ["python", temp_file_name], text=True, capture_output=True, check=True)

        # delete temporary file
        os.remove(temp_file_name)

        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Execution failed: {e.stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


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
    code = req_data.get("code", "")
    programs = req_data.get("programs", "")

    try:
        if code and programs:
            combined_code = f"{programs}{code}"
            # add combined code to async main function launch function
            output = exec_python(combined_code)
            print(output, "-------------------output----------------")
            record_event("observe", "Code was executed")
        else:
            record_event("observe", "No code or program was executed")
    except Exception as e:
        print(f"Exception: {e}")
        record_event("error", None, error=str(e))

    with open("./workspace/events.json", "w") as f:
        json.dump(events_cache, f, indent=2)

    response = {"events": events_cache}
    events_cache = []

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
