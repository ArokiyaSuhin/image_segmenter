# watcher.py
import os
import sys
import time
import logging
import argparse
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Set up logging ---
# This configures how messages are displayed (timestamp, level, message)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class FileCreatedEventHandler(FileSystemEventHandler):
    """
    Handles file creation events and triggers a processor script after a debounce period.
    """
    def __init__(self, processor_script, watch_path, output_path, debounce_seconds=60):
        """
        Initializes the event handler.
        
        Args:
            processor_script (str): The path to the processor script to run.
            watch_path (str): The directory being watched.
            output_path (str): The directory for processed output.
            debounce_seconds (int): How long to wait after the last file creation.
        """
        self.processor_script = processor_script
        self.watch_path = watch_path
        self.output_path = output_path
        self.debounce_seconds = debounce_seconds
        self.last_triggered_time = 0

    def on_created(self, event):
        """
        Called by watchdog when a file or directory is created.
        """
        # We only care about files, not new directories
        if not event.is_directory:
            logging.info(f"File created: {event.src_path}. Resetting debounce timer.")
            # Record the time of this event
            self.last_triggered_time = time.time()

    def run_processor_if_ready(self):
        """
        Checks if the debounce period has passed and then runs the processor script.
        This method should be called periodically (e.g., every second).
        """
        # Check if the trigger has been set and if enough time has passed
        if self.last_triggered_time > 0 and (time.time() - self.last_triggered_time) > self.debounce_seconds:
            logging.info(f"Debounce time of {self.debounce_seconds}s passed. Running processor script.")
            
            try:
                # Use subprocess to call the processor.py script
                # Pass the watch path and output path as arguments
                command = [
                    'python', 
                    self.processor_script, 
                    self.watch_path, 
                    '--output-dir', 
                    self.output_path
                ]
                subprocess.run(command, check=True, capture_output=True, text=True)
                logging.info("Processor script finished successfully.")
            
            except subprocess.CalledProcessError as e:
                # This error happens if the script returns a non-zero exit code (an error)
                logging.error(f"Error running processor script: {e}")
                logging.error(f"Script stderr:\n{e.stderr}")

            except FileNotFoundError:
                logging.error(f"Script not found: Make sure '{self.processor_script}' is accessible.")
            
            finally:
                # Reset the trigger time to prevent running again until a new file is created
                self.last_triggered_time = 0
                logging.info("Watcher is now waiting for new file events.")


def main():
    """Main function to set up and run the directory watcher."""
    # --- Configuration via Command-Line Arguments ---
    parser = argparse.ArgumentParser(
        description="Watch a directory for new files and run a processor script after a period of inactivity."
    )
    parser.add_argument(
        '--watch-dir', 
        type=str, 
        default='my_docs', 
        help="The directory to watch for new files."
    )
    parser.add_argument(
        '--processor-script', 
        type=str, 
        default='processor.py', 
        help="The script to run on the files."
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='finished', 
        help="The directory where processed files will be saved."
    )
    parser.add_argument(
        '--debounce', 
        type=int, 
        default=60, 
        help="Seconds to wait after the last file creation before processing."
    )
    args = parser.parse_args()

    # --- Ensure Directories Exist ---
    # Create the watch and output directories if they don't already exist
    try:
        os.makedirs(args.watch_dir, exist_ok=True)
        os.makedirs(args.output_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directories: {e}")
        sys.exit(1)

    logging.info(f"Watching directory: '{os.path.abspath(args.watch_dir)}'")
    logging.info(f"Press Ctrl+C to stop the watcher.")

    # --- Create and Start the Watchdog Observer ---
    event_handler = FileCreatedEventHandler(
        processor_script=args.processor_script,
        watch_path=args.watch_dir,
        output_path=args.output_dir,
        debounce_seconds=args.debounce
    )
    
    observer = Observer()
    observer.schedule(event_handler, args.watch_dir, recursive=False)
    observer.start()

    # --- Main Loop ---
    # This loop keeps the script alive and periodically checks if the processor should run.
    try:
        while True:
            event_handler.run_processor_if_ready()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Watcher stopped by user.")
        observer.stop()
    finally:
        observer.join() # Wait for the observer thread to finish gracefully


if __name__ == "__main__":
    main()