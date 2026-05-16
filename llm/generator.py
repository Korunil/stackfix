import torch
import re

from threading import Thread
from transformers import TextIteratorStreamer

from config import MAX_NEW_TOKENS

def safe_generate(system_prompt, user_prompt, llm, stream_handler=None, **gen_kwargs):
    
    try:
        # Tokenizer knows exactly which tags (Mistral, Llama, etc.) to use
        tokenizer = llm["tokenizer"]
        model = llm["model"]
        model.eval()
        
        messages = [
            { 
                "role": "system", 
                "content": system_prompt 
            }, 
            { 
                "role": "user", 
                "content": user_prompt 
            } 
        ]
        
        # Automatically add tags [INST] and <s>
        formatted_prompt = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Tokenize the input specifically for the raw model
        inputs = tokenizer(
            formatted_prompt, 
            return_tensors="pt",
            padding=True,
            truncation=True,            
        ).to(model.device)
        print("=========Generator Debug=============")
        print(inputs.keys())

        generation_kwargs = {
            **inputs,
            "max_new_tokens": MAX_NEW_TOKENS,
            "do_sample": True,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.12,
            "use_cache": True,
            "eos_token_id": tokenizer.eos_token_id,
            "pad_token_id": tokenizer.pad_token_id,
        }
        generation_kwargs.update(gen_kwargs)
        
        if stream_handler:
            streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
            generation_kwargs["streamer"] = streamer

            generation_exception = None
            
            def generate_in_thread():                
                nonlocal generation_exception
                
                try:
                    with torch.no_grad():
                        model.generate(**generation_kwargs)
                except Exception as e:
                    generation_exception = e
                    print(f"Generation thread error: {e}")
                finally:
                    streamer.end()
            
            thread = Thread(target=generate_in_thread)
            thread.start()

            tokens = []
            for token in streamer:
                tokens.append(token)
                # Push the token to the Chainlit!
                stream_handler(token)
            generated_text = "".join(tokens)
            
            thread.join()
            if generation_exception:
                raise generation_exception
            
            generated_text = re.sub(r'[ \t]+', ' ', generated_text)
            generated_text = generated_text.replace("``` python", "```python")
            generated_text = generated_text.replace("````", "```")
            
            return generated_text.strip()
        
        else:
            # Fallback for non-streaming
            with torch.no_grad():
                output = model.generate(**generation_kwargs)
            # Slice the output to only get the new tokens (ignoring the prompt)
            new_tokens = output[0][inputs['input_ids'].shape[-1]:]
            return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    
    except Exception as e:        
        return f"❌ Generation Error: {str(e)}"