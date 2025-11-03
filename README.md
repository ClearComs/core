# 📡 ClearComs  

ClearComs is a modular training application designed to help users practice and improve aviation radio communication.  
The project integrates **voice recognition**, **quizzes**, and **flashcards** into a unified platform that allows users to train effectively in ATC and in-flight radio phraseology.  

---

## 🚀 Features  

### 🖥️ Mainpage UI  
- Simple, modular navigation system.  
- Built with **.NET MAUI controls**, allowing multi-platform support.  
- Acts as the central hub to access all modules (Quiz, Flashcards, Voice-to-Text).
- 

### 🎤 Voice-to-Text (Speech Recognition)  
- Uses **OpenAI Whisper** for accurate speech-to-text conversion.  
- Compares spoken phrases with correct responses or flashcards.  
- Helps users practice correct ATC radio phraseology.  

### ❓ Quiz Module  
- Pulls random questions from a database (by section/theme).  
- Displays multiple-choice answers, highlighting correct (green) and incorrect (red).  
- Example implementation: [Get_QA.py](https://github.com/ClearComs/Quiz/blob/main/Get_QA.py).  

### 🃏 Flashcard Module  
- Interactive flashcards with terms & definitions.  
- Flip functionality (word ⇄ definition).  
- Navigate through the flashcard stack easily.  
- Example implementation: [Flashcard Program.cs](https://github.com/ClearComs/core/blob/main/Flashcard-/program.cs).  

---

## 🛠️ Technical Setup  

- **Visual Studio 2022** with Android SDK.  
- **Visual Studio Code** for Python development.  
- **OpenAI & GitHub Copilot**: brainstorming, code framework, debugging, layout suggestions.  
- **Scrum Workflow**:  
  - Used **Trello** for sprint planning & backlog management.  
  - Daily stand-ups to track progress & distribute tasks.  
  - Iterations:  
    - Sprint 1: Project definition & user stories.  
    - Sprint 2: Divide stories & define success criteria.  
    - Sprint 3: Build main modules & set up Git.  
    - Sprint 4: Review progress, report writing.  

---

## 📦 Installation & Usage  

1. Clone the repository:  
   ```bash
   git clone https://github.com/ClearComs/core.git
   cd core
   
   To run the solution, Open in MS Visual Studio
   open solution
   core/GUI/ClearComs.sln
   And here you can interact witht the quiz and flashcard feature

   
2. STT and TTS demo:
   ```bash
   cd STT-TTS_with_example_gui
   python3 gui.py #run gui.py

