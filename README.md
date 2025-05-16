# AI Solar Agent Chat Application

This project demonstrates an AI-powered chat application designed to assist users with solar adoption. It features a JavaScript-based frontend that mimics popular messaging apps, a Python Flask backend, and a LangGraph-powered AI agent system for handling the core logic and API interactions.

## Project Structure (Assumed)

```
.
├── source/                  # Frontend files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── app.py                   # Backend Flask application
├── Langgraph_parts.py       # Core LangGraph agent logic and state definitions
├── requirements.txt         # Python dependencies (recommended)
└── README.md                # This file
```

## Prerequisites

- **Python 3.9+**: Ensure you have Python installed.
- **Pip**: Python package installer.
- **Web Browser**: For viewing the frontend (e.g., Chrome, Firefox, Safari, Edge).
- **LangGraph Parts**: Your `Langgraph_parts.py` file must be correctly set up with your LangGraph application (`app`) and `INITIAL_STATE` defined.
- **Environment Variables**: If your `Langgraph_parts.py` or any backend components rely on environment variables (e.g., API keys, GCP project ID), make sure they are set up in your environment before running the backend.

## Setup

1. **Clone the Repository (if applicable)**  
   If this project is in a Git repository, clone it:

   ```bash
   git clone <your-repository-url>
   cd <project-directory>
   ```

2. **Create a Virtual Environment (Recommended)**  
   It's good practice to use a virtual environment for Python projects.

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

3. **Install Python Dependencies**  
   You should have a `requirements.txt` file listing all necessary Python packages. If not, you'll need to install them manually.  
   Common dependencies for this project would include:

   - `Flask`
   - `flask-cors`
   - `langchain-core`
   - `langgraph`
   - Any specific LLM SDKs (e.g., `langchain-google-vertexai`)
   - Other libraries used in `Langgraph_parts.py`

   Install using `requirements.txt` (if available):

   ```bash
   pip install -r requirements.txt
   ```

   Or install manually (example):

   ```bash
   pip install Flask flask-cors langchain-core langgraph langchain-google-vertexai
   ```

## Running the Application

You need to run the backend server first, and then open the frontend HTML file in your browser. Make sure to set up/check environment variables and change it for your own custom google vertex AI credentials

### 1. Run the Backend (Flask Server)

Navigate to the root folder of the project (where `app.py` is located) in your terminal.  
Execute the following command:

```bash
python app.py
```

This will typically start the Flask development server, usually on [http://127.0.0.1:5000/](http://127.0.0.1:5000/).  
Keep this terminal window open; it's your running backend. You should see log messages here, including confirmation that the server has started and any print statements or errors from the backend.

### 2. Run the Frontend (Chat Interface)

Once the backend server is running:

- Navigate to the `source/` folder (or wherever your `index.html` file is located).
- Directly open the `index.html` file in your web browser.

You can usually do this by double-clicking the `index.html` file.  
Alternatively, right-click on `index.html` and choose "Open with" and select your preferred browser.  
Or, in your browser, use the "File" > "Open File..." menu option and navigate to `index.html`.

The chat interface should load, and the JavaScript in `script.js` will attempt to connect to the backend API (e.g., `http://127.0.0.1:5000/api/chat`).

## How it Works

The frontend (`index.html`, `style.css`, `script.js`) provides the user interface.  
User messages are sent to the backend via HTTP POST requests.

The backend (`app.py`) is a Flask application that:

- Receives messages from the frontend.
- Manages chat session state (in-memory for this example).
- Interacts with the LangGraph agent (`Langgraph_parts.py`) by calling its `invoke()` method with the current session state.
- Returns the AI's response(s) to the frontend.

`Langgraph_parts.py` contains the core AI logic, including the LangGraph definition, agent state, tools, and the LLM integration.

## Troubleshooting

**Backend Not Starting:**  
Check the terminal for Python errors. Ensure all dependencies are installed and environment variables are set.

**Frontend Not Connecting / "Could not connect" errors:**

- Verify the Flask backend is running and accessible (no firewall issues).
- Check the JavaScript console in your browser (usually F12 > Console tab) for network errors or JavaScript errors.
- Ensure the API endpoint URL in `script.js` (e.g., `/api/chat`) correctly matches the route defined in `app.py` and that the backend is running on the expected host and port (default `http://127.0.0.1:5000`).

**LangGraph Errors:**  
Check the Flask backend terminal for tracebacks originating from `Langgraph_parts.py` or the LangGraph library itself. This often relates to state management, tool execution, or LLM API issues.

**CORS Errors:**  
If you see CORS errors in the browser console, ensure `flask-cors` is installed and enabled in the Flask app.