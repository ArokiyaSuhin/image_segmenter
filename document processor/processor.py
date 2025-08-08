import os
import shutil
import argparse
import json
import mimetypes
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def setup_gemini():
    """Configures the Gemini API with the key from environment variables."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY not found in the .env file.")
        print("Please create a file named '.env' in the same directory as the script and add your key like this: API_KEY='Your-Key-Here'")
        exit(1)
    genai.configure(api_key=api_key)

def analyze_document_image(file_path):
    """
    Analyzes a document image using the Gemini API to get its type and serial number.
    """
    print(f"Analyzing {os.path.basename(file_path)}...")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = """
        Analyze the provided document image. Your task is to classify the document and extract its serial number and the site where it has been issued.
        site will be handwritten in feild or a space or a box designated for writing.it is usually with names of ATR,MRS,WTP,STP ,NSTP,KOY,KOD,PY and also accomponied by number such as 60,54,120,110,48 do also note that
        The possible document types are: 'Receipt Memo', 'Cement Issue', 'Diesel Issue', 'Goods Received Note', 'Oil Issue', 'Delivery Challan', or 'Unknown'.
        The serial number should be the most prominent identification number on the form.
        - For 'Goods Received Note', use the 'GRN No.'.
        - For 'Delivery Challan', use the number after '(MTS)'.
        - For 'Diesel Receipt & Issue', use 'S.No.'.
        - For 'Receipt Memo', find the main memo number (e.g., 58653).
        - If no clear serial number is found, use the value 'N/A'.
        Please return a single, raw JSON object with three keys: "documentType" , "serialNumber" and "site". Do not add any extra text, formatting, or markdown.
        """

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            print(f"Skipping non-image file: {file_path}")
            return None

        image_file = genai.upload_file(path=file_path)

        response = model.generate_content(
            [prompt, image_file],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        # Clean up the uploaded file on the server
        genai.delete_file(image_file.name)

        data = json.loads(response.text)
        
        if "documentType" in data and "serialNumber" in data:
            print(f"  -> Detected: Type='{data['documentType']}', S/N='{data['serialNumber']}',site='{data['site']}'")
            return data
        else:
            print(f"  -> Error: API response JSON did not contain the required keys.")
            return None

    except Exception as e:
        print(f"  -> Error during Gemini API call: {e}")
        return None

def process_folder(input_dir, output_dir):
    """Processes all images in a folder, renames, moves, and sorts them."""
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"\nProcessing files from: {input_dir}")
    print(f"Moving sorted files to: {output_dir}\n")

    files_to_process = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    total_files = len(files_to_process)
    success_count = 0
    fail_count = 0

    for filename in files_to_process:
        source_path = os.path.join(input_dir, filename)
        result = analyze_document_image(source_path)

        if result and result.get('documentType') != 'Unknown' and result.get('serialNumber') != 'N/A':
            doc_type = result['documentType']
            serial_num = result['serialNumber']
            
            sanitized_type = doc_type.replace(' ', '_').lower()
            sanitized_serial = ''.join(c for c in str(serial_num) if c.isalnum())
            
            type_dir = os.path.join(output_dir, sanitized_type)
            os.makedirs(type_dir, exist_ok=True)
            
            _, extension = os.path.splitext(filename)
            new_filename = f"{sanitized_type}_{sanitized_serial}{extension}"
            destination_path = os.path.join(type_dir, new_filename)
            
            # --- CHANGE: Move the file instead of copying ---
            shutil.move(source_path, destination_path)
            print(f"  -> Success: Moved to {destination_path}\n")
            success_count += 1
        else:
            # --- CHANGE: Move failed files to a separate directory ---
            print(f"  -> Failed: Could not process '{filename}' correctly. Moving to failed folder.\n")
            fail_count += 1
            error_dir = os.path.join(output_dir, '_failed_to_process')
            os.makedirs(error_dir, exist_ok=True)
            shutil.move(source_path, os.path.join(error_dir, filename))

    print("--- Processing Complete ---")
    print(f"Successfully moved and sorted: {success_count} files.")
    print(f"Failed or skipped: {fail_count} files (moved to '_failed_to_process' folder).")
    print(f"The original input folder '{input_dir}' should now be empty.")
    print(f"Check the '{output_dir}' directory for your sorted files.")

def main():
    """Main function to parse arguments and start the process."""
    parser = argparse.ArgumentParser(
        description="AI Document Sorter CLI",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example usage:
  python process_documents.py /path/to/your/images

This will process all images in the specified folder, move them, and save the
sorted files into a new folder named 'sorted_documents' in your current directory.
The original image folder will be empty after processing.

To specify a different output folder, use the -o flag:
  python process_documents.py /path/to/your/images -o /path/to/output_folder
"""
    )
    parser.add_argument(
        "input_directory",
        help="The path to the folder containing your document images."
    )
    parser.add_argument(
        "-o", "--output_directory",
        default="sorted_documents",
        help="The folder where sorted files will be saved. (default: sorted_documents)"
    )
    args = parser.parse_args()
    
    setup_gemini()
    process_folder(args.input_directory, args.output_directory)

if __name__ == "__main__":
    main()
