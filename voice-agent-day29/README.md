🎙️ AI Voice Agent — 30 Days of AI Challenge
============================================

Welcome to the AI Voice Agent, a project built as part of the 30 Days of AI Voice Agents Challenge.Over 30 days, we incrementally designed, built, tested, and deployed a voice-powered AI agent that can handle multiple skills, integrate with APIs, and provide a real-world assistant experience.

Journey Recap (Day-by-Day Highlights)
-------------------------------------

*   Day 1–5: Setup environment, basic voice agent structure, and hello-world interactions.
    
*   Day 6–10: Added text-to-speech and speech-to-text pipeline with robust error handling.
    
*   Day 11–15: Introduced modular skills (Weather, News, Jokes, Q&A).
    
*   Day 16–20: Improved UX with multi-skill orchestration and fallback responses.
    
*   Day 21–25: Integrated APIs (news/weather) and user config system for API keys.
    
*   Day 26–28: UI revamp with configurable settings, animations, and polish.
    
*   Day 29: Final documentation and polish (this README).
    
*   Day 30: Final showcase and reflection.
    

Features
--------

*   Voice input and output: Speak naturally, get AI-powered responses.
    
*   Weather updates: Real-time weather via API.
    
*   News headlines: Latest stories delivered instantly.
    
*   Jokes on demand: Lighthearted responses.
    
*   General Q&A: AI-driven knowledge answers.
    
*   Custom API keys: Users can plug in their own API keys directly in UI.
    
*   Modern UI: Clean, animated interface for better usability.
    
*   Modular architecture: Easy to add or remove skills.
    

Tech Stack
----------

*   Backend: Python (Flask or FastAPI depending on setup)
    
*   Frontend: React, Tailwind, shadcn/ui
    
*   APIs: OpenAI, Weather, News
    
*   Deployment: Gunicorn, Docker, Vercel/Render
    

Installation and Usage
----------------------

1.  Clone the repositorygit clone [https://github.com/your-username/voice-agent.git](https://github.com/your-username/voice-agent.git?utm_source=chatgpt.com)cd voice-agent
    
2.  Setup environmentpython -m venv .venvsource .venv/bin/activatepip install -r requirements.txt
    
3.  Run locallygunicorn app:app
    
4.  Access in browser at [http://127.0.0.1:8000](http://127.0.0.1:8000?utm_source=chatgpt.com)
    

Roadmap
-------

*   Add memory for contextual conversations.
    
*   Multi-language support.
    
*   Mobile version of the app.
    

Contributing
------------

Contributions, issues, and feature requests are welcome.Feel free to open a PR to suggest improvements.

Acknowledgements
----------------

*   30 Days of AI Voice Agents Challenge organizers for structuring the journey.
    
*   OpenAI and community contributors for APIs, tutorials, and support.
    

Connect
-------

*   LinkedIn: [https://linkedin.com/in/saymanlal](https://linkedin.com/in/saymanlal?utm_source=chatgpt.com)
    
*   Blog Post: [https://medium.com/@worksofsayman/️-8939a43df6a2](https://medium.com/@worksofsayman/️-8939a43df6a2?utm_source=chatgpt.com)