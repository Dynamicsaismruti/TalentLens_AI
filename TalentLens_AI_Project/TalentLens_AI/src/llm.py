import ollama


MODEL_NAME = "gemma3:1b"

# Maximum time Python will wait for Ollama
OLLAMA_TIMEOUT = 30


def safe_generate(prompt: str, fallback: str = "") -> str:
    """
    Generate text using the local Ollama LLM.

    A timeout is used so the Streamlit application
    does not remain stuck indefinitely.
    """

    try:

        client = ollama.Client(
            host="http://localhost:11434",
            timeout=OLLAMA_TIMEOUT
        )

        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2,
                "num_predict": 300
            },
            keep_alive="5m"
        )

        answer = response["message"]["content"]

        if answer and answer.strip():
            return answer.strip()

        return fallback

    except Exception as e:

        print(f"Ollama error: {e}")

        return fallback