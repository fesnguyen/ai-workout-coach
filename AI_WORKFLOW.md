# AI_WORKFLOW.md

## Tools Used

I used **OpenAI Chat, Gemini Chat, Claude Chat, and GitHub Copilot - Code Completion** throughout this exercise.

* **OpenAI Chat, Gemini Chat, and Claude Chat** were mainly used for generating code, quick reviews, suggestions, and validating ideas.
* **OpenAI Chat** was my primary AI partner during the implementation. I used it for designing the architecture, evaluating different approaches, arguing and debating the best solution, retrieving information, generating code, fixing bugs, and reviewing implementation decisions.
* **GitHub Copilot** was mainly used to speed up coding by generating boilerplate code and assisting while implementing features.

### Feature I Didn't Use
#### GitHub Copilot Agent

**Reason**

* I intentionally chose not to use GitHub Copilot Agent during this exercise.

* Although it can quickly generate complete features (for example, implementing an entire RAG pipeline with Chroma or generating a complete memory module), I believe this level of automation reduces my control over the design and implementation process. It becomes more difficult to evaluate architectural decisions, understand the generated code in depth, and ensure that every component aligns with my intended design.

* In a long-term production environment, I think Copilot Agent is most effective after the project's architecture, design decisions, coding standards, and development guidelines have already been established. At that stage, it can significantly accelerate implementation while still operating within well-defined constraints.

* For this take-home exercise, however, I wanted the implementation process to accurately reflect my own engineering decisions and problem-solving approach. Since part of the evaluation is likely based on how I designed and built the solution, relying on an autonomous coding agent could have obscured that process and made it harder for reviewers to assess my reasoning and technical judgment.

* For these reasons, I deliberately excluded GitHub Copilot Agent from my development workflow while still using GitHub Copilot's code completion features to improve productivity.

---

## Examples Where I Rejected AI Suggestions

### 1. Rejecting an unnecessary abstraction

**ChatGPT suggested:**

Creating a new abstraction layer to handle an exception case.

**Why I rejected it:**

I felt this would introduce additional abstractions and schemas that made the codebase more complex without providing enough practical value. The exception was isolated and did not justify a new architecture.

**What I did instead:**

I designed a simpler solution that handled the case within the existing structure.

**Result:**

After discussing the alternative, ChatGPT agreed with my approach and responded:

> "I actually love your approach more."

---

### 2. Rejecting the old Message-Centric conversation strategy

**ChatGPT suggested:**

Following a **Message-Centric** strategy and suggesting me manage a consistent conversation in ourside, which would introduce db management, schema, service and manually control conversation id.

**Why I rejected it:**

Modern OpenAI APIs are no longer strictly Message-Centric. They have shifted toward an **Item-Centric** approach, where OpenAI manages conversation flow and caching internally. Because of this, introducing additional schemas and conversation management on my side would only add unnecessary complexity.

**What I did instead:**

I adopted the newer Item-Centric approach and kept the implementation much simpler by relying on the API's built-in conversation management.

**Result:**

After further discussion, ChatGPT understood the reasoning and shifted to recommending the modern approach instead.

---

## Prompting Strategy

My general prompting strategy is to provide:

* Clear and precise instructions.
* Concrete examples whenever possible.
* The current context and circumstances.
* Images when they help explain the problem.

I also have a personal prompting strategy that I repeatedly remind the AI of during long conversations:

* "I am always looking for modern approaches, best practices, and gold-standard solutions. I am eager to learn new architectures, technologies, and implementation patterns", this will encourage chatbox to introduce newest architecture, design, approach,... which sometime it follow our understand too strictly.
* "Make sure any information you provide is acurate and align with newest updates, gimme the link reference to prove it's true" when I need some essential info to be absolutely accurate.

These reminders help keep the discussion aligned with my learning goals throughout long conversations.

---

## Reflection on Guardrails

AI chatbots were particularly helpful when designing the guardrail architecture. They served as discussion partners for brainstorming, debating trade-offs, and verifying design decisions.

They helped me think through what the system should refuse and why, and I generally did not encounter any significant issues with ChatGPT's suggestions in this area. The discussions were valuable in refining the overall guardrail design and validating the implementation approach.
