import time
import assemblyai as aai
import threading

# Global lock to synchronize file access
file_lock = threading.Lock()
transcription = ""
sent_length = 0
last_update_time = time.time()
aai.settings.api_key = "e8349e0c311e419ab4a0993dcade5866"
SILENCE_THRESHOLD = 0.5  # 700ms of silence

def write_to_message_file(message):
    """Write the transcribed message to message.txt with proper synchronization."""
    global file_lock
    try:
        with file_lock:  # Ensure only one thread writes at a time
            with open("messages.txt", "a") as f:
                f.write(f"{message}\n")
    except Exception as e:
        print(f"Error writing to message.txt: {e}")
def paste_and_send():
    global sent_length

    new_text = transcription[sent_length:]

    if new_text:
        write_to_message_file(new_text)
        sent_length = len(transcription)
        last_update_time = time.time()


def start_transcription():
    transcriber = aai.RealtimeTranscriber(
        sample_rate=44100,  # Sample rate for better quality
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        end_utterance_silence_threshold=700  # Silence threshold
    )
    transcriber.connect()
    microphone_stream = aai.extras.MicrophoneStream(sample_rate=44100, device_index=1)
    transcriber.stream(microphone_stream)


def on_data(transcript: aai.RealtimeTranscript):
    global transcription
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        # Add new text to transcription
        transcription += transcript.text + " "  # Add space between utterances
        last_update_time = time.time()
        print(transcription)


def clear():
    global transcription, sent_length
    transcription = ""
    sent_length = 0
    last_update_time = time.time()
    print("Transcription cleared")


# Callback functions for error and session closure
def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)


def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session ID:", session_opened.session_id)


def on_close():
    print("Session closed.")


def start_speechtotext():
    transcription_thread = threading.Thread(target=start_transcription)
    transcription_thread.start()


def monitor_clipboard():
    global transcription, last_update_time, sent_length
    while True:
        current_time = time.time()
        if len(transcription) > sent_length and current_time - last_update_time > SILENCE_THRESHOLD:
            paste_and_send()
        time.sleep(0.1)


def main():
    start_speechtotext()
    monitor_clipboard()


if __name__ == "__main__":
    main()
