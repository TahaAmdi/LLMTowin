Below is a **Markdown-ready** Poetry cheat sheet you can paste directly into your `README.md`.

---

# 🧰 Poetry Cheat Sheet — Install, Use, Troubleshoot (Windows-friendly)

## 0) Health checks

```powershell
poetry --version
poetry env info
poetry show --top-level
poetry run python -V
poetry run python -c "import sys,site; print(sys.version); print(site.getsitepackages())"
```

---

## 1) Install & PATH (Windows)

**Common fix when `poetry` isn’t recognized**

```powershell
(Get-Command poetry).Source
where poetry
# If needed, add to PATH (session)
$env:Path += ";$env:APPDATA\Python\Scripts"; $env:Path += ";$env:APPDATA\pypoetry\venv\Scripts"
```

**Install specific Poetry version with pip**

```powershell
py -3 -m pip install --user "poetry==1.8.4"   # or 1.8.3
poetry --version
```

**If `setx` errors because PATH is long**

```powershell
# Set only the target path (avoids “Default option is not allowed more than '2' time(s)”)
setx PATH "C:\Users\<User>\AppData\Roaming\Python\Scripts"
```

---

## 2) Python version & venv

**Version constraints in `pyproject.toml`**

```toml
[tool.poetry.dependencies]
# choose one:
python = "^3.11"      # >=3.11,<4.0
# python = "~3.11"    # >=3.11,<3.12
# python = "3.11.8"   # exactly 3.11.8
```

**Create venv with a specific Python**

```powershell
poetry env use 3.11.8
# or exact path:
poetry env use "C:\Users\<User>\AppData\Local\Programs\Python\Python311\python.exe"
```

**Keep venv inside the project (`.venv/`)**

```powershell
poetry config virtualenvs.in-project true --local
poetry env remove python
poetry env use 3.11.8
poetry install
poetry env info   # Path should be .\.venv
```

---

## 3) Dependencies & locking

**Concepts**

* `pyproject.toml` = what you want (ranges).
* `poetry.lock` = exactly what’s installed (pinned, reproducible).

**Commands**

```powershell
poetry install                 # from lock; creates lock if missing
poetry add fastapi             # add & update toml+lock
poetry remove fastapi          # remove
poetry update fastapi          # update within constraints
poetry lock --no-update        # rebuild lock from toml without bumping versions
```

> Example: with Python 3.11, `numpy` must be ≥1.26. If you wrote `^1.19`, the resolver will pick a compatible higher version (e.g., 1.26.4) and pin it in the lock.

---

## 4) Running code in the venv

**Three reliable ways**

```powershell
# A) enter the venv shell
poetry shell
python script.py
exit

# B) run without entering
poetry run python script.py

# C) activate .venv manually (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
python script.py
```

**Fix for `ModuleNotFoundError: No module named 'X'`**
Run using one of the methods above (you were likely using the global Python).

---

## 5) VS Code setup (per-project)

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true
}
```

* Use **Run Python File** / **F5** (Python extension).
* If you use **Code Runner** and want it to use `.venv`:

```json
{
  "code-runner.runInTerminal": true,
  "code-runner.executorMap": {
    "python": "${workspaceFolder}\\.venv\\Scripts\\python.exe -u"
  }
}
```

---

## 6) Frequent warnings & quick fixes

**Warning:** *“The current project could not be installed: No file/folder found for package …”*

* You’re trying to install the project as a package without package structure.

  * If you only want dependency management:

    ```toml
    [tool.poetry]
    package-mode = false
    ```

    or run `poetry install --no-root`
  * If you want a package, use a `src` layout:

    ```
    src/your_pkg/__init__.py
    ```

    and in `pyproject.toml`:

    ```toml
    packages = [{ include = "your_pkg", from = "src" }]
    ```

**Error:** *“Group(s) not found: aws (via --without)”*

* By default only the main group installs. Use:

  ```powershell
  poetry install               # main only
  poetry install --with dev    # add dev
  poetry install --with dev,aws
  ```

**`poetry show python` says not found**

* Python isn’t a PyPI package. See the interpreter used with:

  ```powershell
  poetry env info
  ```

**Installed version differs from `toml` range**

* The lock wins. Align by:

  ```powershell
  poetry add fastapi==0.110.0
  # or
  poetry update fastapi
  ```

---

## 7) Handy snippets

**List versions programmatically**

```python
from importlib.metadata import version, PackageNotFoundError
for name in ["numpy","requests","fastapi","pydantic","starlette"]:
    try:
        print(name, version(name))
    except PackageNotFoundError:
        print(name, "NOT INSTALLED")
```

**Show current Python path & site-packages**

```powershell
poetry run python -c "import sys,site; print(sys.executable); print(site.getsitepackages())"
```

**Switch quickly between Pythons**

```powershell
poetry env use 3.11.8
poetry env use "C:\Path\To\Another\python.exe"
```

---

## 8) Minimal `pyproject.toml` (dependency-only)

```toml
[tool.poetry]
name = "my-proj"
version = "0.1.0"
readme = "README.md"
package-mode = false

[tool.poetry.dependencies]
python = "~3.11"
fastapi = "^0.119.0"
numpy = "^1.26"
requests = "^2.32"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

**Tip:** For rock-solid reproducibility, keep `.venv` inside the project and always run via VS Code’s selected interpreter or `poetry run …`.
