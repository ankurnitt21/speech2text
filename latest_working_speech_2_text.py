import time
import pyautogui
import assemblyai as aai
import threading
import keyboard
from datetime import datetime

transcription = ""
sent_length = 0
last_update_time = time.time()
aai.settings.api_key = "e8349e0c311e419ab4a0993dcade5866"
SILENCE_THRESHOLD = 0.7  # 700ms of silence


import pyautogui
from PIL import Image

def is_chatgpt_typing():
    """Check typing status by taking a full-screen screenshot and looking for typing indicator."""
    try:
        # Take a full-screen screenshot
        screenshot = pyautogui.screenshot()

        # Define the region around send button coordinates (left, top, width, height)
        send_button_region = (
            831 - 20,  # left = 831 (adjusted for padding)
            930 - 20,  # top = 930 (adjusted for padding)
            70,        # width = 70px (adjusted to fit the typing indicator)
            70         # height = 70px (adjusted to fit the typing indicator)
        )

        # Crop the screenshot to the specified region
        cropped_screenshot = screenshot.crop((
            send_button_region[0],
            send_button_region[1],
            send_button_region[0] + send_button_region[2],
            send_button_region[1] + send_button_region[3]
        ))

        # Save the cropped screenshot for debugging purposes
        cropped_screenshot.save("cropped_screenshot.png")
        #print("Cropped screenshot saved as 'cropped_screenshot.png'.")

        # Look for typing indicator in the cropped region
        indicator = pyautogui.locateOnScreen('typing_indicator.png',
                                             region=send_button_region,
                                             confidence=0.9,  # Confidence level
                                             grayscale=False)  # Disable grayscale for color images

        if indicator:
            #print("Typing indicator found:", indicator)
            return True
        else:
            #print("Typing indicator NOT found.")
            return False

    except Exception as e:
        #print(f"Detection error: {e}")
        return False

def paste_and_send():
    global sent_length
    original_pos = pyautogui.position()
    new_text = transcription[sent_length:]

    if new_text:
        try:
            pyautogui.click(491, 887)
            pyautogui.write(new_text, interval=0)
            pyautogui.click(841, 940)
            sent_length = len(transcription)
            last_update_time = time.time()
        finally:
            pyautogui.moveTo(original_pos)


def start_transcription():
    transcriber = aai.RealtimeTranscriber(
        sample_rate=44100,  # Sample rate for better quality
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        end_utterance_silence_threshold=400  # Silence threshold
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
        if not is_chatgpt_typing():
            if len(transcription) > sent_length and current_time - last_update_time > SILENCE_THRESHOLD:
                paste_and_send()
        time.sleep(0.1)


def main():
    start_speechtotext()
    monitor_clipboard()
    #is_chatgpt_typing()

if __name__ == "__main__":
    main()
