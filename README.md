# OpenAI VoiceStream

OpenAI VoiceStream is a Python library that provides real-time text-to-speech functionality using the OpenAI API. It allows you to process text and token streams and generate audio output on-the-fly, making it suitable for integration with language models that generate responses in segments.

## Features

- Real-time text-to-speech conversion
- Support for processing text and token streams
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Thread-safe processing for smooth operation
- Audio fading to avoid abrupt stops

## Installation

You can install OpenAI VoiceStream using pip:

```bash
pip install openai-voicestream
```

## Usage

### Prerequisites

Before using OpenAI VoiceStream, make sure you have an OpenAI API key. Set the API key as an environment variable:

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Example Code

Here's 2 examples of how to use OpenAI VoiceStream passing in text and for a token stream:
```python
import os
import time
from openai_voicestream import VoiceProcessor

# Retrieve your OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the VoiceProcessor with the API key and desired voice
processor = VoiceProcessor(api_key, voice="nova")  # Using the "nova" voice

# Example text with paragraphs to be processed
text = """This is an example using the nova voice.

The nova voice provides a different tone and style compared to the default voice.

You can experiment with different voices to find the one that suits your needs."""

# Add the text to the processing queue
processor.add_text_to_queue(text)

# Wait for all processing to complete before exiting
processor.wait_for_completion()
```


```python
import os
import time
from openai_voicestream import VoiceProcessor

# Retrieve your OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the VoiceProcessor with the API key and desired voice
processor = VoiceProcessor(api_key, voice="shimmer")  # Using the "shimmer" voice

# Example tokens being added to the processing queue
tokens = [
    "This is an example of processing a stream of tokens.",
    " The tokens are gradually added to the processor,",
    " simulating a real-time scenario where text is generated incrementally.",
    "\n\nThe processor will handle the tokens and generate audio on-the-fly,",
    " providing a seamless text-to-speech experience."
]

# Process the tokens in a streaming manner (this can be replaced with an tokenstream)
for token in tokens:
    processor.add_token(token)

# Finalize any remaining tokens in the buffer
processor.finalize_tokens()

# Wait for all processing to complete before exiting
processor.wait_for_completion()
```

## API Reference

### VoiceProcessor

The main class for processing text and generating audio.

#### `__init__(self, api_key, voice='alloy')`

Initializes the VoiceProcessor with the provided API key and voice.

- `api_key` (str): The API key for accessing the OpenAI API.
- `voice` (str or int): The voice to use for text-to-speech. Can be specified by name or index.

#### `add_text_to_queue(self, text)`

Adds text to the processing queue.

- `text` (str): The text to add to the queue.

#### `add_token(self, token)`

Adds a token to the buffer and processes it if needed.

- `token` (str): The token to add to the buffer.

#### `finalize_tokens(self)`

Finalizes any remaining tokens in the buffer.

#### `wait_for_completion(self)`

Waits for all sentences to be processed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## Acknowledgements

OpenAI VoiceStream is built using the OpenAI API and relies on the following libraries:

- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [httpx](https://www.python-httpx.org/)

## Troubleshooting

If you encounter any issues while using OpenAI VoiceStream, here are a few things you can try:

- Make sure you have set the `OPENAI_API_KEY` environment variable correctly with your OpenAI API key.
- Check that you have a stable internet connection to communicate with the OpenAI API.
- If you encounter any errors or exceptions, please check the error message and consult the documentation or seek support.

## FAQ

### Can I use OpenAI VoiceStream for commercial purposes?

Yes, you can use OpenAI VoiceStream for commercial purposes, subject to the terms and conditions of the OpenAI API usage. Make sure to review and comply with OpenAI's usage policies.

### How can I customize the voice output?

OpenAI VoiceStream provides multiple voice options that you can choose from. You can specify the desired voice by passing the voice name or index to the `VoiceProcessor` constructor. Available voices include: alloy, echo, fable, onyx, nova, and shimmer.

### Can I control the speed or pitch of the generated audio?

Currently, OpenAI VoiceStream does not provide direct control over the speed or pitch of the generated audio. The audio is generated based on the selected voice and the input text. If you require more advanced audio customization, you may need to explore other text-to-speech libraries or APIs.

### Is there a limit on the amount of text I can process?

The amount of text you can process depends on the limitations of the OpenAI API. OpenAI VoiceStream processes text in chunks, so it can handle larger text inputs by breaking them down into smaller segments. However, keep in mind that processing large amounts of text may result in longer processing times and higher API usage.

## Support

If you have any questions, issues, or feature requests, please open an issue on the [GitHub repository](https://github.com/kristofferv98/openai-voicestream). I appreciate your feedback and will do our best to assist you.

