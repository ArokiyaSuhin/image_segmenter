AI Document Sorter
The AI Document Sorter is a powerful command-line utility that uses Google's Gemini AI to automatically analyze, rename, and organize a folder of document images. It intelligently identifies the document type and its serial number, then sorts the files into a clean, structured directory.FeaturesAI-Powered Classification: Leverages the gemini-2.5-flash model for fast and accurate document analysis.Intelligent Data Extraction: Extracts both the document type (e.g., 'Receipt Memo', 'Delivery Challan') and its unique serial number.Automated File Organization: Renames files to a standard document-type_serial-number.ext format and sorts them into sub-folders based on type.Robust Error Handling: Automatically moves any files that cannot be processed into a _failed_to_process folder for manual review, ensuring no data is lost.Secure API Key Management: Uses a .env file to keep your Google API key secure and out of the source code.User-Friendly CLI: Provides a simple command-line interface with clear instructions for easy operation.


Prerequisites
Before you begin, ensure you have the following:Python: Version 3.7 or newer.Google 
AI Studio API Key: A valid API key is required to use the Gemini model. You can get one from Google AI Studio.

Project Dependencies: The script requires two Python libraries.Setup & InstallationFollow these steps to get the project up and running.

1. Clone or Download the RepositoryFirst, get the project files onto your local machine.

2. Install DependenciesIt's highly recommended to create a virtual environment to keep project dependencies isolated.# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate it
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Next, install the required Python libraries from the requirements.txt file.# Install all required packages
pip install -r requirements.txt

If you don't have a requirements.txt file, you can create one with the following content:google-generativeai
python-dotenv

Then run the pip install command above.

3. Configure Your API KeyThe script loads your API key from a local environment file.Create a file named .env in the root directory of the project.Open the .env file and add your API key in the following format:API_KEY='Your-Google-API-Key-Here'


How to Use

Run the script from your terminal, providing the path to the folder containing your document images.Basic UsageThis command will process images from the my_docs folder and save the sorted files into a new folder named sorted_documents in the current directory.

python processor.py path/to/your/my_docs


Example:If your my_docs folder is inside the project directory:

python processor.py my_docs


Specifying an Output DirectoryUse the -o or --output_directory flag to specify a custom folder for the sorted files.python processor.py path/to/your/my_docs -o path/to/your/output_folder


Example:python processor.py my_docs -o finished_documents

Output StructureThe script will generate an output folder with the following structure. Each document type gets its own sub-folder, and any files that could not be processed are placed in _failed_to_process.sorted_documents/
├── cement_issue/
│   └── cement_issue_12345.pdf
│
├── delivery_challan/
│   ├── delivery_challan_67890.jpg
│   └── delivery_challan_67891.png
│
├── goods_received_note/
│   └── goods_received_note_ABC01.jpg
│
└── _failed_to_process/
    └── confusing_document.jpg
TroubleshootingError: API_KEY not found: Ensure you have created the .env file in the correct directory and that the key is formatted as API_KEY='Your-Key-Here'.Error: Input directory not found: Check that the path to your input directory is correct. If the folder is in the same directory as the script, just use its name (e.g., my_docs) without any leading slashes.Files in _failed_to_process: This can happen if the AI could not confidently determine the document type or serial number, or if the file is not a supported image format.




@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


for devs


pip install google-generativeai python-dotenv


.env
API_KEY='Your-Google-API-Key-Here'


requirements.txt
google-generativeai
python-dotenv


pip install -r requirements.txt



go to the directory of the project folder


and run
python processor.py my_docs -o output_folder


for watchdog
pip install watchdog


