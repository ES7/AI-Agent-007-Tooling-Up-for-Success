# AI-Agent-007-Tooling-Up-for-Success
High Prep Problem Statement by DevRev at InterIIT TechMeet 12.0

## How to run this project

### 1) Clone the repo
```bash
git clone https://github.com/ES7/AI-Agent-007-Tooling-Up-for-Success.git
cd AI-Agent-007-Tooling-Up-for-Success
```

### 2) Create & activate virtual environment (recommended)
**Windows (PowerShell)**
```bash
python -m venv .devrev
.\.devrev\Scripts\Activate.ps1
```

**Windows (CMD)**
```bash
python -m venv .devrev
.\.devrev\Scripts\activate
```

**Mac/Linux**
```python3 -m venv .devrev
source .devrev/bin/activate
```

### 3) Install dependencies
```pip install -r requirements.txt```

### 4) Set OpenAI API Key
**Windows (PowerShell)**
```$env:OPENAI_API_KEY="YOUR_OPENAI_KEY_HERE"```

**Windows (CMD)**
```set OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE```

**Mac/Linux**
```export OPENAI_API_KEY="YOUR_OPENAI_KEY_HERE"```

### 5) Run the agent
```python main.py --query "Prioritize my P0 issues and add them to the current sprint"```

### 6) Clear memory (optional)
```python main.py --clear```
