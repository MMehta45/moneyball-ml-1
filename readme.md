Moneyball Academics: AI-Optimized Degree Planner
================================================

Overview
--------

Build a engine that will build your mathematically perfect 4 year degree by **Maximizing your GPA** (by avoiding notoriously tough classes/professors) and **Minimizing your Tuition** (by strategically routing core classes to community college during the summer).

The MVP (Minimum Viable Product)
--------------------------------

Our MVP is broken down into three core pillars:

**1\. The Map (Data & Graphing)**

*   We map the UTD Computer Science degree plan as a **Directed Acyclic Graph (DAG)**.
    
*   Every class is a node. Prerequisites are the arrows connecting them.
    
*   Nodes are loaded with historical data: Average GPA (from Nebula Labs), Credit Hours, and Transferability status.
    
*   We use "Dummy Nodes" for Free Electives to avoid scraping thousands of useless classes.
    

**2\. The Brain (The ML Engine)**

*   A **Genetic Algorithm (GA)** that generates, scores, and creates 4-year schedules.
    
*   **Hard Constraints (Rules of Physics):** The AI is physically blocked from breaking prerequisites or dropping a student below their scholarship minimum credit hours.
    
*   **Soft Constraints (The Fitness Function):** The AI scores schedules based on user preferences. It actively penalizes "Burnout" (taking 19 hours of brutal classes) and rewards tuition efficiency (maximizing flat-rate UTD block tuition while utilizing summer community college).
    

**3\. The Face (Interactive UI)**

*   A web dashboard where students input their current transcript and scholarship minimums.
    
*   **Live Sliders:** Users drag a slider to dictate their risk tolerance (e.g., "70% Save Money / 30% Pad GPA").
    
*   **Visual Output:** Instead of a boring spreadsheet, the backend sends the AI's perfect schedule to the frontend to be rendered as an interactive, branching tree map.
    

Stretch Goals
-------------

*   **Pessimistic Optimizer:** Train the AI to assume the student gets the _worst_ professor for every class, building "bulletproof" schedules.
    
*   **Prerequisite Explainer:** Click a class node to see exactly why it was placed in that specific semester.
    
*   **Export to PDF:** Allow users to download their Moneyball schedule for their real academic advisor.
    
*   **Containerization:** Dockerize the API and UI for easy deployment.
    

Tech Stack
----------

*   **Data Prep:** Python, Pandas
    
*   **Graphing Logic:** NetworkX (Python)
    
*   **ML Engine:** DEAP (Distributed Evolutionary Algorithms in Python)
    
*   **Backend API:** FastAPI (Python)
    
*   **Frontend UI:** React (Next.js or Vite) + React Flow (for the visual tree)
    
*   **Styling:** Tailwind CSS
    

Timeline (5-Week Sprint)
------------------------

_Subject to change We go phase by phase but everyone gets to work on everything._

*   **Week 1 (The Map):** Extract UTDgrades data, build the networkx DAG, map all prerequisites, and compile transfer rules.
    
*   **Week 2 (The Brain - Pt 1):** Set up the DEAP Genetic Algorithm loop. Define the math for the Fitness Function (GPA vs. Cost).
    
*   **Week 3 (The Brain - Pt 2):** Code the Penalty functions (Scholarship minimums, Burnout thresholds, Prerequisite enforcers). Freeze the ML model.
    
*   **Week 4 (The Face):** Build the FastAPI endpoints. Connect the React Flow frontend.
    
*   **Week 5 (Polish & Pitch):** Connect the UI sliders to the live ML engine. Clean bugs. Prep the live demo.
    

Branching Rules
---------------

**Main Branch**

*   main must always remain stable and demo-ready.
    
*   **NO direct commits to main.**
    
*   Only merged via approved Pull Requests.
    

**Creating a Feature Branch**Every feature must be developed on a new branch created from main.

*   Branch naming convention: feature\_name
    
*   Examples: data\_cleaning, genetic\_loop, fastapi\_routes, react\_flow\_ui
    

**How to Create a Branch:**

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git checkout main  git pull origin main  git checkout -b genetic_loop   `

⚙️ Development & PR Process
---------------------------

1.  Create a new branch from main.
    
2.  Implement your feature.
    
3.  Push the branch to GitHub.
    
4.  Open a **Pull Request (PR)** into main.
    

**Pull Request Rules:**

*   PRs must include a clear description of what the code does.
    
*   If it's UI, include a screenshot.
    
*   If it's ML math, explain the logic briefly.
    

**Review & Merge Process:**

*   I will review the code to prevent integration nightmares.
    
*   **No self-merging.** I will merge into main once it's approved.
    

📚 Resources
------------

These are just high level overview for the project, I will add more as we go on.

**Everyone Should Look At:**

*   [Git & GitHub Crash Course (15 mins)](https://www.youtube.com/watch?v=USjZcfj8yxE)
    
*   [What is a Directed Acyclic Graph?](https://www.youtube.com/watch?v=1Yh5S-S6wsI)
    
*   [How Genetic Algorithms Work (Simple overview)](https://www.youtube.com/watch?v=uQj5UNhCPuo)