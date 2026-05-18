import asyncio
import chainlit as cl
from chainlit.input_widget import Select, Checkbox

from llm.llm import load_llm
from llm.generator import safe_generate
from pipeline.debug_pipeline import DebugPipeline

from config import *
import preload

# BLOCK STARTUP: For a local tool, it's safer to build/load the indexes 
# before starting the server so the UI doesn't crash on empty variables.
print("Initializing StackFix Knowledge Base...")
preload.preload_retriever()

@cl.on_chat_start
async def start():
    
    # Show an initial loading state
    initial_msg = cl.Message(content="🛠️ Loading 🐞 StackFix...")
    await initial_msg.send()
    
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="AI Models",
                values=["mistral", "mistral2", "llama"],
                initial_index=0,
            ),
            Checkbox(
                id="Quantization",
                label="Enable Quantization",
                initial=True,
            ),
        ]
    ).send()
    
    model_choice = settings["Model"]
    quantization = settings["Quantization"]

    llm = await asyncio.to_thread(load_llm, model_choice, MODEL_MAP, quantization)

    pipeline = DebugPipeline(preload.GLOBAL_RETRIEVER, llm)

    cl.user_session.set("pipeline", pipeline)
    await initial_msg.remove()
    await cl.Message(
        content=( 
            "# 🐞 StackFix \n" 
            "### Hybrid AI Debugging Agent \n\n"
            "Intelligently switches between local retrieval "
            "and live web reasoning for accurate debugging help.\n\n"
            "Paste your error, traceback, compiler issue, "
            "or describe the bug you're facing." 
        ) 
    ).send()


@cl.on_message
async def main(message: cl.Message):

    pipeline = cl.user_session.get("pipeline")
    
    # Show a loading spinner so the user knows it's thinking
    loading_msg = cl.Message(content="🔍 Analyzing query...")
    await loading_msg.send()

    # 1. GET THE STATE FROM THE PIPELINE (Fast)
    state = await asyncio.to_thread(pipeline.prepare, message.content)
    
    # 2. SEND THE HEADER IMMEDIATELY
    header = (f"**⚙️ Route:** `{'internet' if state['route'] == 'fallback' else state['route'].upper()}` |" 
    f"**📊 Local Match:** `{state['confidence']:.2f}`\n\n---\n\n")
    msg = cl.Message(content=header)
    await loading_msg.remove()
    await msg.send()
    
    # 3a. GET ACTIVE EVENT LOOP
    loop = asyncio.get_running_loop()

    # 3b. DEFINE THE STREAM CATCHER
    def on_token(token):
        # Safely bridges the background generation thread to the async Chainlit UI
        asyncio.run_coroutine_threadsafe(
            msg.stream_token(token),
            loop
        )

    # 4. GENERATE AND STREAM THE ANSWER
    answer = await asyncio.to_thread( 
        safe_generate, 
        state["system_prompt"], 
        state["user_prompt"], 
        pipeline.llm, 
        stream_handler=on_token, 
        **state["config"] 
    )
    
    pipeline.memory.add(message.content, answer)
    
    final_content = msg.content + "\n\n"

    # Add Citations to the bottom of the message
    if state.get("citations"):
        final_content += "---\n### 📚 Sources:\n"
        SOURCE_META = {
            "github": ("🐙", "GitHub"),
            "github_api": ("🐙", "GitHub API"),
            "stackoverflow": ("💬", "StackOverflow"),
            "docs": ("📘", "Docs"),
            "huggingface": ("🤗", "HuggingFace"),
            "web": ("🌐", "Web")
        }
        
        for i, cite in enumerate(state["citations"], 1):
            title = cite.get("title", "Unknown Title")
            
            # Check the flag!
            if cite.get("is_external"):
                url = cite.get("url") or "#"
                source_type = cite.get("source_type", "web")
                
                icon, label = SOURCE_META.get(
                    source_type,
                    ("🌐", "Web")
                )
                final_content += (
                    f"**[{i}]** {icon} "
                    f"[{title}]({url}) "
                    f"*({label})*\n"
                )
            else:
                score = cite.get("score", 0.0)
                icon, label = SOURCE_META.get("docs", ("🌐", "Web"))
                final_content += (
                    f"**[{i}]** {icon} "
                    f"[{title}] "
                    f"*({label}) "
                    f"*(Relevance: {score:.4f})*\n"
                )

    # Update the message one last time to snap the citations into place at the bottom
    msg.content = final_content
    
    await msg.update()
