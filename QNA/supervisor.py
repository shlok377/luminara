import ollama
import json
from typing import List, Dict, Any

SUPERVISOR_PROMPT = """
You are an expert editor. Your task is to review the provided list of questions and answers.
1. Check for incomplete sentences in the 'question', 'answer', or 'context_snippet'.
2. Complete any cut-off text logically based on the context provided within the item.
3. Fix grammatical errors.
4. Return the output in the EXACT same JSON structure (list of objects).
"""

def supervise_quiz(questions: List[Dict[str, Any]], model: str = "llama3.1:8b") -> List[Dict[str, Any]]:
    """
    Refines the list of questions/answers.
    """
    print("  - Running AI Supervision on Quiz...")
    
    refined_questions = []
    
    # Process in batches
    batch_size = 5 # Questions can be long, keep batch small
    for i in range(0, len(questions), batch_size):
        batch = questions[i : i + batch_size] 
        
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': SUPERVISOR_PROMPT},
                    {'role': 'user', 'content': f"Fix and complete sentences in this JSON list:\n\n{json.dumps(batch, ensure_ascii=False)}"}
                ],
                format='json',
            )
            
            content = response['message']['content']
            fixed_batch = json.loads(content)
            
            # Robust extraction of list from response
            if isinstance(fixed_batch, dict):
                # Check for common wrapper keys
                for key in ["questions", "items", "data"]:
                    if key in fixed_batch and isinstance(fixed_batch[key], list):
                        fixed_batch = fixed_batch[key]
                        break
                else:
                    # If still a dict and matches the schema of a single question, wrap it
                    if "question" in fixed_batch:
                         fixed_batch = [fixed_batch]
                    # fallback: try values
                    elif any(isinstance(v, list) for v in fixed_batch.values()):
                         for v in fixed_batch.values():
                             if isinstance(v, list):
                                 fixed_batch = v
                                 break

            if isinstance(fixed_batch, list):
                refined_questions.extend(fixed_batch)
            else:
                refined_questions.extend(batch)
                
        except Exception as e:
            print(f"    ! Error supervising batch: {e}")
            refined_questions.extend(batch)
            
    return refined_questions
