import ast
from fastapi import FastAPI, Request
import json
import os
import subprocess
import tempfile
import llama_cpp.server
from autoimport import fix_code
import isort

app = FastAPI()
events_cache = []


# def find_missing_imports(code_str):
#     parsed_code = ast.parse("code.py")
#     missing_imports = []
#     for node in ast.walk(parsed_code):
#         if isinstance(node, ast.Name) and node.id not in globals():
#             missing_imports.append(node.id)
#     return missing_imports


def exec_python(code):
    try:
        code_after_imports = fix_code(code)
        sorted_code = isort.code(code_after_imports)
       # save code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(sorted_code)
            temp_file_name = f.name

        print(f"{sorted_code}")

        # execute code
        result = subprocess.run(
            ["python", temp_file_name], text=True, capture_output=True, check=True)

        # delete temporary file
        os.remove(temp_file_name)

        return {
            "is_executed": True,
            "output": f"{result.stdout}"
        }
    except subprocess.CalledProcessError as e:
        return {
            "is_executed": False,
            "output": f"{e.stderr}"
        }
    except Exception as e:
        return {
            "is_executed": False,
            "output": f"{str(e)}"
        }


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
            execution = exec_python(combined_code)
            if execution["is_executed"]:
                if execution["output"] == "":
                    record_event(
                        "observe", "Code was executed successfully, but not printed anything.")
                else:
                    record_event("observe", execution["output"])
            else:
                record_event("observe", "Code was not executed successfully",
                             error=execution["output"])
        else:
            record_event("observe", "No code or program was executed")
    except Exception as e:
        print(f"Exception: {e}")
        record_event("error", "Error", error=str(e))

    with open("./logs/events.json", "w") as f:
        json.dump(events_cache, f, indent=2)

    response = {"events": events_cache}
    # events_cache = []

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

# print(exec_python(
#     """
# def fetch_data(url):
#     response = requests.get(url)
#     data = response.json()
#     return data

# async def find_papers_and_create_table():
#     # Step 1: Fetch data from arxiv API for LLM-related papers in the last week
#     url = "https://api.arxiv.org/query"
#     params = {
#         'search_query': 'LLM',
#         'sortBy': 'publishedDate',
#         'after': datetime.datetime.now() - datetime.timedelta(days=7),
#         'max_results': 100
#     }
#     response = requests.get(url, params=params)
#     data = response.json()['records']

#     # Step 2: Parse the fetched data using BeautifulSoup
#     soup = BeautifulSoup(data, 'html.parser')

#     # Step 3: Extract the domains from the paper titles
#     domains = set()
#     for paper in soup.find_all('item'):
#         title = paper.title.text
#         domain = re.search(
#             r'[a-zA-Z0-9]+\.(?:com|net|org|edu|gov|mil|io|co|uk)', title).group()
#         if domain:
#             domains.add(domain)

#     # Step 4: Count the number of papers in each domain
#     counts = {domain: 0 for domain in domains}
#     for domain in domains:
#         for paper in soup.find_all('item'):
#             if domain in paper.title.text:
#                 counts[domain] += 1

#     # Step 5: Create a markdown table with columns: Domain, Number of Papers
#     table = "| Domain | Number of Papers |\n"
#     for domain, count in counts.items():
#         table += f"| {domain} | {count} |\n"

#     # Step 6: Sort the table by the Number of Papers column in descending order
#     sorted_table = sorted(counts.items(), key=lambda x: x[1], reverse=True)
#     for domain, count in sorted_table:
#         table += f"| {domain} | {count} |\n"

#     # Step 7: Save the sorted table to a file
#     with open('papers_by_domains.md', 'w') as f:
#         f.write(table)

# asyncio.run(find_papers_and_create_table())
# """
# ))
