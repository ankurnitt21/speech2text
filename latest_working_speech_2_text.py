import time
import pyautogui
import assemblyai as aai
import threading
import keyboard

transcription = ""
sent_length = 0
last_update_time = 0
aai.settings.api_key = "e8349e0c311e419ab4a0993dcade5866"


def is_chatgpt_typing():
    try:
        screenshot = pyautogui.screenshot()
        send_button_region = (811, 910, 90, 90)
        cropped_screenshot = screenshot.crop(send_button_region)
        indicator = pyautogui.locateOnScreen('typing_indicator.png',
                                             region=send_button_region,
                                             confidence=0.9)
        return bool(indicator)
    except Exception:
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
        finally:
            pyautogui.moveTo(original_pos)

def start_transcription():
    transcriber = aai.RealtimeTranscriber(
        sample_rate=44100,  # Sample rate for better quality
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        end_utterance_silence_threshold=600  # Silence threshold
    )
    transcriber.connect()
    microphone_stream = aai.extras.MicrophoneStream(sample_rate=44100,device_index=1)
    transcriber.stream(microphone_stream)

def on_data(transcript: aai.RealtimeTranscript):
    global transcription
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        # Add new text to transcription
        transcription += transcript.text + " "  # Add space between utterances
        print(transcription)

def clear():
    global transcription, sent_length
    transcription = ""
    sent_length = 0
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
    global transcription
    while True:
        if not is_chatgpt_typing():
            paste_and_send()
            time.sleep(0.1)



def main():

    start_speechtotext()

    monitor_clipboard()

if __name__ == "__main__":
    main()
