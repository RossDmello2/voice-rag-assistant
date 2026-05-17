# Standard Operating Procedure (SOP): Ultimate Voice Agent

Welcome to the Ultimate Voice Agent! This guide is designed for beginners and laymen to understand, configure, and run the voice agent step-by-step. 

## 1. What is the Ultimate Voice Agent?

The Ultimate Voice Agent is an advanced, multi-agent AI system that you can talk to in real-time. It has two "brains":
1. **The Fast Path**: For simple questions (like "Hello", "How are you?"), it responds instantly.
2. **The ULTRATHINK Path**: For complex reasoning (like math or coding), a "Supervisor" agent detects the complexity and routes it to a deep-thinking agent. The UI will glow **purple** while it thinks before finally speaking the answer.

---

## 2. Directory Structure

Before running the agent, you need to be in the correct folder. 

**Your Target Directory:**
`C:\Users\rossd\Dropbox\PC\Downloads\rag-demo-n8n-to-web\chatbot_static_files_fixed\voice agent\voice agent migration\voice_agent\voice_agent_backend`

Inside this folder, you will find:
- `app/` - The core logic, agents, and API routes.
- `frontend/` - The user interface (HTML, CSS, JS) that you interact with in the browser.
- `.env` - (Required) Your secret configuration file.
- `start_server.bat` - The script you click or run to start the agent.

---

## 3. Configuration & Prerequisites

Before running the agent for the first time, ensure you have your environment set up.

### Environment Variables (`.env` file)
Copy the root `.env.example` file to `voice_agent_backend/.env`. Open `voice_agent_backend/.env` with Notepad and ensure it contains your API keys:
```env
GROQ_API_KEY=
```
*(The system uses Groq to generate fast LLM responses. Make sure your Groq account is funded or active).*

---

## 4. How to Run the Agent

Follow these exact steps to start the server:

### Step 1: Open your Terminal (PowerShell)
Open PowerShell on your Windows computer.

### Step 2: Navigate to the Backend Directory
Type the following command and press **Enter**:
```powershell
cd "C:\Users\rossd\Dropbox\PC\Downloads\rag-demo-n8n-to-web\chatbot_static_files_fixed\voice agent\voice agent migration\voice_agent\voice_agent_backend"
```

### Step 3: Run the Start Script
Type the following command and press **Enter**:
```powershell
.\start_server.bat
```

### Step 4: Access the Frontend
Once the server starts, you will see logs appearing in your terminal. 
Open your web browser (Chrome/Edge) and go to:
**`http://127.0.0.1:50501`**

---

## 5. How to Use the Voice Agent (The UI)

Once you open the browser link, you will see the Agent's interface.
- **The Orb**: In the center of the screen is a glowing orb.
  - **Blue/Dim**: Idle.
  - **Orange**: Processing a standard fast-path response.
  - **Purple**: "ULTRATHINK" Mode. The agent is tackling a complex problem and thinking deeply.
  - **Green**: Speaking to you.
- **Microphone Button**: Click this to start talking. Speak naturally!
- **Text Input**: If you prefer not to speak, you can type your question at the bottom and hit Send.

---

## 6. Common Warnings & Terminal Logs (Troubleshooting)

When running `.\start_server.bat`, you will see a lot of text scrolling by in the terminal. **Do not panic if you see yellow warnings!** Here is what they mean:

> [!WARNING]
> **`[W:onnxruntime:Default... OP Conv... running in Fallback mode. May be extremely slow.]`**
> **What it means:** The Text-to-Speech (TTS) engine (Kokoro) uses ONNX runtime to generate audio. Since this system is running on a GTX 1650 (which has limited VRAM), some audio generation layers fall back to the CPU instead of the GPU. 
> **Action:** Ignore it. The audio will still generate, it just might take a fraction of a second longer.

> [!WARNING]
> **`WARNING:phonemizer:words count mismatch on 100.0% of the lines`**
> **What it means:** The text-to-speech engine parses numbers and symbols slightly differently than standard words.
> **Action:** Ignore it. It is completely harmless and normal.

> [!NOTE]
> **`INFO: 127.0.0.1:50501 - "POST /chat/stream HTTP/1.1" 200 OK`**
> **What it means:** The frontend successfully communicated with the backend and received a response.
> **Action:** None. This means your agent is working perfectly!

### How to Stop the Server
When you are done using the agent, go back to your PowerShell window and press **`Ctrl + C`**. It will ask `Terminate batch job (Y/N)?`. Type **`y`** and press Enter.
