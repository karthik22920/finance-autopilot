import requests


def query_ollama(prompt: str, model: str = "mistral", timeout: int = 180) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "").strip()

        if not text:
            return "Ollama returned an empty response."
        return text

    except requests.exceptions.ConnectionError:
        return (
            "Ollama is not reachable on localhost:11434. "
            "Start Ollama and make sure the selected model is available."
        )
    except requests.exceptions.Timeout:
        return "Ollama request timed out before a response was generated."
    except Exception as e:
        return f"Ollama request failed: {e}"