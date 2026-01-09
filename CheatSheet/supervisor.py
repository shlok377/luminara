import ollama
import json
from typing import Dict, Any, List

SUPERVISOR_PROMPT = """
You are an expert editor. Your task is to review the provided structured notes (definitions, comparisons, timelines, concepts) and fix any incomplete sentences, grammatical errors, or awkward phrasing.
Ensure the content remains accurate to the source material but is polished and complete.
Return the output in the EXACT same JSON structure as the input. Do not add or remove items, just refine the text values.
"""

def supervise_cheatsheet(data: Dict[str, Any], model: str = "llama3.1:8b") -> Dict[str, Any]:
    """
    Sends the merged data to the LLM for a final polish/fix pass.
    To avoid context limits, we process each category separately or in batches.
    """
    print("  - Running AI Supervision on Notes...")
    
    refined_data = {
        "definitions": [],
        "comparisons": [],
        "timelines": [],
        "concepts": []
    }

    # Process each category
    for category in ["definitions", "comparisons", "timelines", "concepts"]:
        items = data.get(category, [])
        if not items:
            continue
            
        # We'll process items in batches of 10 to ensure quality and fit in context
        batch_size = 10
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            
            try:
                response = ollama.chat(
                    model=model,
                    messages=[
                        {'role': 'system', 'content': SUPERVISOR_PROMPT},
                        {'role': 'user', 'content': f"Fix and polish this JSON list of {category}:\n\n{json.dumps(batch, ensure_ascii=False)}"}
                    ],
                    format='json',
                )
                
                content = response['message']['content']
                fixed_batch = json.loads(content)
                
                # Handling potential structure mismatch from LLM
                if isinstance(fixed_batch, dict):
                    # sometimes LLM wraps it in a key like {"definitions": [...]} 
                    values = list(fixed_batch.values())
                    if values and isinstance(values[0], list):
                        fixed_batch = values[0]
                    else:
                        # If it returned a dict but not the list we wanted, fallback to original
                        fixed_batch = batch

                if isinstance(fixed_batch, list):
                    refined_data[category].extend(fixed_batch)
                else:
                    refined_data[category].extend(batch)
                    
            except Exception as e:
                print(f"    ! Error supervising batch in {category}: {e}")
                # Fallback to original data on error
                refined_data[category].extend(batch)

    # Copy over any other keys that might exist (though merger usually only outputs these 4)
    for k, v in data.items():
        if k not in refined_data:
            refined_data[k] = v
            
    return refined_data
