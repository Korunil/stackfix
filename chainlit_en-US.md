# Welcome to 🐞 StackFix!

Hi there! 👋 I am excited to have you on board. 

StackFix is a AI-powered hybrid debugging agent that intelligently switches between local semantic retrieval and live web reasoning to solve developer issues efficiently. 

Instead of blindly guessing, StackFix actively cross-references your bugs against 1.1 million verified StackOverflow solutions. 

### ⚡ What makes StackFix different?
* **Smart Routing:** If your bug is new, the engine automatically abandons its local database and searches the live internet (GitHub/Web) for zero-day fixes.
* **Privacy First:** Your code runs through local models right on your machine.
* **Minimal Fixes:** We prioritize exact code fixes over giant, unnecessary rewrites.

### StackFix is built using:
- Retrieval-Augmented Generation (RAG)
- semantic retrieval
- CrossEncoder reranking
- intelligent routing
- local LLM inference

### It helps debug:
- stack traces
- import errors
- dependency conflicts
- framework/runtime issues
- compiler errors

---

## Example Queries

```bash
ModuleNotFoundError: No module named 'dotenv'
TypeError: unsupported operand type(s)
DistributionNotFound after upgrading pip
No module named 'langchain_huggingface'
```