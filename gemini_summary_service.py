from collections.abc import Callable

from google import genai
from google.genai import types


class GeminiSummaryService:

  def stream_summary(
      self, youtube_url: str, api_key: str, on_text: Callable[[str], None]
  ):
    client = genai.Client(api_key=api_key)
    contents = self._create_contents(youtube_url)
    config = self._create_config()

    for chunk in client.models.generate_content_stream(
        model="gemini-flash-lite-latest", contents=contents, config=config
    ):
      if text := chunk.text:
        on_text(text)

  def _create_contents(self, youtube_url: str):
    return [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(file_uri=youtube_url, mime_type="audio/mp4"),
                types.Part.from_text(
                    text="Generate the detailed summary of this video following the system instructions."
                ),
            ],
        )
    ]

  def _create_config(self):
    return types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="MEDIUM"),
        temperature=0.0,
        media_resolution="MEDIA_RESOLUTION_MEDIUM",
        audio_transcription_config=types.AudioTranscriptionConfig(),
        tools=[
            types.Tool(url_context=types.UrlContext())
        ],
        system_instruction=[
            types.Part.from_text(text="""Whenever I post a YouTube link, generate a detailed summary of the video. 

Rules:
1. Strictly ignore all sponsor segments, ads, and mid-roll promotions.
2. Match the language of the video (e.g., English audio = English summary; German audio = German summary).
3. Structure the summary clearly using headings and bullet points with timestamps. 
   - CRITICAL: Do NOT just describe *what* the video talks about (e.g., avoid phrases like "The speaker discusses X" or "Predictions regarding Y"). Instead, extract the **actual points, arguments, facts, and opinions** made by the speaker. State *what* they predict, not just *that* they are predicting.
4. FACTUAL ACCURACY: Only mention names of persons, products, or channels that are EXPLICITLY spoken in the audio. If a person is not named by speech, refer to them as 'the speaker' or 'the guest'. Never guess names.
5. After the headings and bullet points write a seperate Conclusion : A short wrap-up of the speaker's core message or final verdict.
""")
        ],
    )