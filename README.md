Command to run: .venv\Scripts\python.exe -m flask run --port 5001



# Smart Quiz Generator (Web)

A modern quiz web app (Flask) that fetches questions from the Open Trivia Database.

## Quick start (Windows - PowerShell)

1. Open PowerShell and change to the project directory:

```powershell
cd "d:\Quiz Generator using Python"
```

2. (Optional) Activate the virtual environment if you created one:

```powershell
. .venv\Scripts\Activate.ps1
```

3. Install dependencies (if needed):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
# or if not using the venv python: python -m pip install -r requirements.txt
```

4. Run the web server:

```powershell
# Use the venv python if available
.venv\Scripts\python.exe app.py
# OR
python app.py
```

5. Open the app in your browser:

```
http://127.0.0.1:5000
```

## Notes
- If you prefer `flask run`, set `FLASK_APP=app.py` then `flask run`.
- If the app cannot reach the Open Trivia API, it will use `questions.json` as a fallback.
- To stop the server press `Ctrl+C` in the terminal.
