from pathlib import Path
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from webdriver_manager.chrome import ChromeDriverManager
from chrome_controller import ChromeController, Config, EventHandler, InputHandler
import signal
import sys
import os
import logging
import threading

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = Config()
    controller = ChromeController(config)
    shutdown_event = threading.Event()
    
    if not controller.initialize():
        print("Failed to initialize Chrome controller")
        return

    event_handler = EventHandler(controller)
    event_handler.start()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while not shutdown_event.is_set():
            try:
                shutdown_event.wait(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
    finally:
        event_handler.stop()
        try:
            controller.cleanup()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()