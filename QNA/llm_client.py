import ollama
import json
from typing import List, Dict, Any

def generate_questions(
    chunk_text: str, 
    question_type: str, 
    char_limit: int, 
    model: str = "llama3.1:8b"
) -> List[Dict[str, Any]]:
    """
    Generates questions and answers from a text chunk using Ollama.
    """
    
    prompt = f"""
You are an expert educational content generator. Analyze the provided text and generate as many {question_type} questions as possible.
    
    Goal: comprehensive and exhaustive extraction. 
    - Cover every single fact, date, definition, concept, and detail in the text.
    - Do not summarize multiple points into one question; create separate questions for each specific piece of information.
    - Generate as many questions as the text allows, regardless of variety.
    
    Focus on extracting:
    - Definitions
    - Comparisons
    - Timelines
    - Causes and Effects
    - Processes
    - Relationships
    - Important Concepts
    - Minor details and specific facts

    Constraints:
    1. The 'type' field must be '{question_type}'.
    2. The 'answer' field must be approximately {char_limit} characters long.
    3. Include a short 'context_snippet' from the text that supports the answer.
    4. Return ONLY a valid JSON list of objects.

    Output Schema:
    [
        {{
            "question": "The question text",
            "answer": "The answer text",
            "type": "{question_type}",
            "context_snippet": "Relevant text from source"
        }}
    ]
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': f"Generate questions from this text:\n\n{chunk_text}"}
            ],
            format='json',
        )
        
        content = response['message']['content']
        data = json.loads(content)
        
        # Ensure it's a list (Ollama might sometimes return a dict wrapping the list)
        if isinstance(data, dict):
            # Try to find a list value if the root is a dict
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return [data] # Return the dict as a single item list if no list found
            
        return data

    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def generate_questions_from_notes(
    notes_data: Dict[str, Any],
    question_type: str,
    char_limit: int,
    model: str = "llama3.1:8b"
) -> List[Dict[str, Any]]:
    """
    Generates questions based on the structured data from CheatSheet (definitions, concepts, etc.).
    """
    # Flatten important notes into a string context
    context_parts = []
    
    if "definitions" in notes_data:
        for item in notes_data["definitions"][:20]: # Limit to top 20 to avoid context overflow
            context_parts.append(f"Definition: {item.get('term')} - {item.get('definition')}")
            
    if "concepts" in notes_data:
        for item in notes_data["concepts"][:10]:
            context_parts.append(f"Concept: {item.get('name')} - {item.get('explanation')}")
            
    if "comparisons" in notes_data:
        for item in notes_data["comparisons"][:10]:
            context_parts.append(f"Comparison: {item.get('subject_a')} vs {item.get('subject_b')} - {item.get('difference_or_similarity')}")

    if not context_parts:
        return []

    context_text = "\n".join(context_parts)
    
    prompt = f"""
You are an expert quiz generator. Using ONLY the provided notes, generate a set of {question_type} questions.

    Source Material:
{context_text}

    Goal: Create unique questions derived directly from these definitions, concepts, and comparisons.
    - Generate at least 10-15 questions if possible.
    
    Constraints:
    1. The 'type' field must be '{question_type}'.
    2. The 'answer' field must be approximately {char_limit} characters long.
    3. Use the provided note content as the 'context_snippet'.
    4. Return ONLY a valid JSON list of objects.

    Output Schema:
    [
        {{
            "question": "The question text",
            "answer": "The answer text",
            "type": "{question_type}",
            "context_snippet": "Relevant text from source"
        }}
    ]
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': "You are a quiz generator."},
                {'role': 'user', 'content': prompt}
            ],
            format='json',
        )
        
        content = response['message']['content']
        data = json.loads(content)
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return [data]
            
        return data

    except Exception as e:
        print(f"Error generating questions from notes: {e}")
        return []
