import os
import textwrap

# --- Helper function to clear the console ---
def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Dictionary of Projects and their Advanced Prompts ---
# Each key is the project title, and the value is a detailed prompt for an AI model.
projects = {
    "1. Web Scraper for E-commerce Price Tracking": """
    Generate a Python script for an advanced E-commerce Price Tracker.

    The application should have a Graphical User Interface (GUI) using Tkinter. It must allow users to:
    1.  Add products to track by pasting their URLs.
    2.  Automatically detect the e-commerce site (support for Amazon, eBay, and Alibaba) and find the price and product name elements.
    3.  Store the list of tracked products locally in a SQLite database, including URL, product name, initial price, and current price.
    4.  Display the tracked products in a listbox or treeview, showing the name, current price, and the date it was last checked.
    5.  Include a "Check Prices" button to manually trigger a scrape for all products.
    6.  Implement a background scheduling feature (using the `schedule` library) to automatically check prices at a user-defined interval (e.g., every 6 hours).
    7.  If a price has dropped below its previous lowest recorded price, send a desktop notification to the user.
    8.  Use the `requests` and `BeautifulSoup4` libraries for scraping. Include robust error handling for network issues, CAPTCHAs, and changes in website structure. Add realistic user-agents to avoid being blocked.
    """,
    "2. Personal Finance Tracker with Budgeting Features": """
    Create a comprehensive Personal Finance Tracker application in Python with a GUI using PyQt6 or Tkinter.

    The application must include these advanced features:
    1.  **Transaction Management**: Users can add, edit, and delete income and expense transactions. Each transaction should have a date, description, category, and amount.
    2.  **SQLite Database**: All data should be stored in a local SQLite database for persistence.
    3.  **Budgeting**: Allow users to set monthly budgets for different categories (e.g., 'Groceries', 'Rent', 'Entertainment').
    4.  **Dashboard and Reporting**: The main window should feature a dashboard that displays:
        -   Current month's total income vs. total expenses.
        -   A progress bar for each budget category, showing how much has been spent.
        -   A pie chart (using Matplotlib) visualizing expenses by category for the current month.
    5.  **Data Visualization**: A separate 'Reports' tab where users can generate and view historical data, such as bar charts of monthly income/expenses over the year.
    6.  **CSV Import/Export**: Functionality to import transactions from a CSV file (from a bank statement) and export reports to a CSV file.
    7.  **Categorization**: A settings panel where users can manage (add/remove/edit) spending and income categories.
    """,
    "3. Automated Social Media Poster": """
    Generate a Python script for an Automated Social Media Poster.

    The tool needs a simple GUI (Tkinter) to manage a content schedule. It should support posting to Twitter and a Facebook Page.

    Key Features:
    1.  **API Integration**: Use the official Twitter API (via `tweepy`) and Facebook Graph API (via `facebook-sdk`). The application must handle authentication securely, allowing users to input their API keys and access tokens, which are then saved in an encrypted configuration file.
    2.  **Content Scheduling**: Users should be able to write a post, optionally attach an image (via a file dialog), and schedule it to be posted at a specific date and time.
    3.  **Scheduling Queue**: The main UI should display a table of all scheduled posts, showing the content, target platform (Twitter/Facebook), and scheduled time.
    4.  **Background Scheduler**: Use the `schedule` library to run a background thread that continuously checks if any posts are due to be published.
    5.  **Multi-Platform Posting**: Allow users to select whether a post goes to Twitter, Facebook, or both simultaneously.
    6.  **Error Logging**: Log all activities, including successful posts and any API errors, to a file named `poster.log`.
    """,
    "4. Machine Learning Model for Image Classification": """
    Generate a Python script that trains and deploys a machine learning model for image classification.

    The project should consist of two parts: a training script and a GUI application for inference.

    **Part 1: Training Script (`train_model.py`)**
    1.  Use the TensorFlow or PyTorch library.
    2.  Use a well-known dataset like CIFAR-10.
    3.  Implement a Convolutional Neural Network (CNN).
    4.  The script should train the model on the dataset and then save the trained model weights to a file (e.g., `image_classifier.h5` for TensorFlow).

    **Part 2: GUI Application (`classifier_app.py`)**
    1.  Build a GUI using Tkinter or PyQt6.
    2.  The GUI must have a button to "Load Image" which opens a file dialog.
    3.  Once an image is loaded, display it in the GUI.
    4.  Include a "Classify" button that loads the pre-trained model, preprocesses the selected image to match the model's input requirements, and performs inference.
    5.  Display the top 3 predicted class labels and their corresponding probabilities.
    """,
    "5. Task Management Application with a GUI": """
    Create an advanced Task Management Application using Python and the PyQt6 framework.

    The application should function as a complete To-Do list manager with professional features.

    Features:
    1.  **Modern UI**: Use PyQt6 for a clean and modern user interface.
    2.  **Task Properties**: Each task should have a title, a detailed description, a due date, a priority level (Low, Medium, High), and a status (To-Do, In Progress, Done).
    3.  **Project-Based Organization**: Allow users to create different "Projects" and assign tasks to them. The UI should have a panel on the left to list projects, and selecting a project filters the tasks shown.
    4.  **Database Storage**: Use SQLite to store all projects and tasks, ensuring data persistence between sessions.
    5.  **Filtering and Sorting**: Users should be able to filter tasks by status or priority and sort them by due date.
    6.  **Due Date Notifications**: Implement a system that checks for tasks due today upon application startup and shows a desktop notification.
    7.  **Drag-and-Drop**: Allow users to change the status of a task by dragging and dropping it between columns representing 'To-Do', 'In Progress', and 'Done'.
    """,
    "6. Simple Chatbot using Natural Language Processing": """
    Build a GUI-based chatbot in Python. The chatbot should be more advanced than a simple rule-based system.

    Frameworks and Libraries:
    -   GUI: **Tkinter**
    -   NLP: **NLTK** or **spaCy** for text processing, and **scikit-learn** for the classification model.

    Functionality:
    1.  **Intents and Responses**: Create a JSON file (`intents.json`) that defines patterns of user inputs and corresponding bot responses. Include at least 10 intents like 'greeting', 'goodbye', 'about', 'help', 'hours', 'location', etc.
    2.  **Model Training**:
        -   The script should first process the `intents.json` file.
        -   Use NLTK/spaCy to tokenize, lemmatize, and convert the text patterns into a numerical format (Bag of Words).
        -   Train a simple classification model (like a Feedforward Neural Network using TensorFlow/Keras or a classic ML model) to predict the intent based on user input.
        -   Save the trained model and vectorizer to disk.
    3.  **GUI Chat Interface**:
        -   A main window with a read-only text area to display the conversation history.
        -   An entry box for the user to type their message.
        -   When the user sends a message, the application loads the trained model, processes the input, predicts the intent, and displays a random appropriate response from the `intents.json` file.
    """,
    "7. File Organizer Script": """
    Create an advanced, GUI-based File Organizer script in Python.

    This tool should help users automatically clean up specified directories (like 'Downloads').

    GUI (Tkinter or PyQt6):
    1.  An input field for the user to select a target directory to organize.
    2.  A configuration panel where the user can define rules. For example, mapping file extensions (`.pdf`, `.docx`) to folder names ('Documents').
    3.  A "Preview" button that scans the directory and shows the user which files will be moved and to where, without actually moving them.
    4.  An "Organize" button to execute the file moving and folder creation operations.
    5.  A "Watch Directory" checkbox. If checked, the script will run in the background (using the `watchdog` library) and automatically organize new files as they are added to the directory.
    6.  A log window to display all actions taken (e.g., "Moved 'report.docx' to 'Documents'").
    7.  The rules and target directory should be saved to a JSON config file to persist between sessions.
    """,
    "8. Password Generator and Manager": """
    Create a secure Password Generator and Manager application with a Python GUI (PyQt6 or Tkinter).

    Security is the top priority.

    Features:
    1.  **Master Password**: The application must be locked behind a single master password.
    2.  **Encryption**: Use the `cryptography` library. All stored passwords must be encrypted using Fernet (AES-based encryption). The key for encryption should be derived from the user's master password using a key derivation function like PBKDF2.
    3.  **Password Generation**: A tool to generate strong, random passwords. The user should be able to specify the length and choose whether to include uppercase letters, numbers, and symbols.
    4.  **Password Storage**: A secure vault to store website names, usernames, and their corresponding encrypted passwords. Use a SQLite database to store this data.
    5.  **GUI Vault**: The main window should display the list of saved credentials (website and username only). When a user clicks an entry, they should be prompted to re-enter their master password to view or copy the saved password.
    6.  **Copy to Clipboard**: A button to copy a password to the clipboard. The clipboard should be automatically cleared after 30 seconds for security.
    """,
    "9. Simple Web Server using Flask or Django": """
    Create a simple dynamic website using Python's Flask framework.

    The website will be a personal blog.

    Project Requirements:
    1.  **Backend (Flask)**:
        -   Use Flask to build the web server.
        -   Implement routing for the home page, individual post pages, and an 'About' page.
        -   Use a SQLite database with SQLAlchemy as the ORM to manage blog posts.
        -   The `Post` model should include an id, title, content, author, and date_posted.
        -   Create a simple admin interface (or a password-protected route) to add, edit, and delete blog posts.
    2.  **Frontend (HTML/CSS)**:
        -   Use Jinja2 templates to render the HTML pages.
        -   Create a base template (`layout.html`) that other pages extend.
        -   The home page should list all blog posts with their titles and a short snippet. Clicking a title leads to the full post.
        -   Use a clean and simple CSS framework like Bootstrap for styling.
    3.  **Structure**: The project should be well-organized with separate folders for templates, static files, and the main application logic.
    """,
    "10. Email Automation Script": """
    Create a GUI application for email automation in Python.

    This tool will allow users to send personalized bulk emails from a Gmail account.

    GUI (Tkinter):
    1.  **Authentication**: Fields for the user's Gmail address and an App Password. The credentials should be handled securely.
    2.  **Recipient List**: A button to load a list of recipients from a CSV file. The CSV file should contain columns like `name` and `email`.
    3.  **Email Template**: A large text box for the email subject and another for the email body. The user can use placeholders like `{name}` in the template, which will be replaced with data from the CSV file for each recipient.
    4.  **Attachments**: A button to attach a file to the emails.
    5.  **Preview**: A "Preview" button that shows how the email will look for the first recipient in the list.
    6.  **Send Emails**: A "Send" button that iterates through the CSV list, personalizes the email for each recipient, and sends it using Python's `smtplib` and `email` modules. Include a small delay between sending emails to avoid being flagged as spam.
    7.  **Progress Bar**: A progress bar that updates as the emails are sent.
    """,
    "11. Currency Converter Application": """
    Generate a Python script for a Currency Converter application with a GUI (Tkinter or PyQt6).

    The application must fetch real-time exchange rates from a public API.

    Features:
    1.  **Real-time Rates**: Use a free currency exchange rate API (like exchangerate-api.com or openexchangerates.org). The application should fetch the latest rates on startup.
    2.  **GUI**:
        -   An input field for the amount to be converted.
        -   Two dropdown menus (comboboxes) for selecting the 'From' currency and the 'To' currency. These dropdowns should be populated dynamically with the currency codes fetched from the API.
        -   A "Convert" button.
        -   A label to display the result of the conversion, formatted clearly (e.g., "100 USD = 85.50 EUR").
    3.  **Offline Mode**: If the API call fails (e.g., no internet), the application should notify the user and can optionally use the last successfully fetched rates, clearly indicating they are not live.
    4.  **Swap Currencies**: A "Swap" button to quickly interchange the 'From' and 'To' currencies.
    5.  **Error Handling**: Implement robust error handling for API failures, invalid user input (e.g., non-numeric amount), etc.
    """,
    "12. To-Do List Application with Cloud Sync": """
    Create a To-Do List application in Python that syncs across devices using a simple cloud service.

    Project Components:
    1.  **GUI (PyQt6)**: A clean, modern interface where users can add, edit, delete, and mark tasks as complete. Completed tasks should be visually distinct (e.g., grayed out with a strikethrough).
    2.  **Local Storage (SQLite)**: Tasks are always stored in a local SQLite database for fast, offline access. Each task should have a unique ID, content, and a status (complete/incomplete).
    3.  **Cloud Sync (Firebase Realtime Database)**:
        -   Use Google's Firebase Realtime Database as the backend.
        -   The application should authenticate with Firebase.
        -   When the application starts, it fetches the latest data from Firebase and syncs it with the local SQLite database, handling any conflicts (e.g., last-write-wins).
        -   Any change made in the GUI (add, edit, delete) is pushed to both the local SQLite DB and the Firebase Realtime Database.
    4.  **Sync Status**: The GUI should have a status indicator showing the last sync time and whether it's currently connected to the cloud.
    """,
    "13. Simple Game using Pygame": """
    Create a complete 2D arcade-style game using Python's Pygame library.

    Game Concept: **Space Invaders Clone**

    Key Features:
    1.  **Player Control**: The player controls a spaceship at the bottom of the screen that can move left and right and fire projectiles upwards.
    2.  **Enemies**: A grid of alien enemies moves horizontally across the screen. When the grid reaches the edge, it drops down and reverses direction.
    3.  **Shooting**: The player can shoot to destroy aliens. The aliens can also randomly drop bombs downwards.
    4.  **Lives and Score**: The player starts with 3 lives. A life is lost if the player's ship is hit by a bomb or if the aliens reach the bottom of the screen. The score increases for each alien destroyed.
    5.  **Increasing Difficulty**: The speed of the aliens increases as more of them are defeated.
    6.  **Sound Effects and Music**: Include sound effects for shooting, explosions, and a background music loop. Use `.wav` or `.ogg` files.
    7.  **Game States**: Implement proper game states: a start screen, the main game loop, and a 'Game Over' screen that displays the final score.
    8.  **Graphics**: Use simple sprite graphics for the player, aliens, and projectiles.
    """,
    "14. Data Analysis and Visualization of Stock Market Data": """
    Generate a Python script that performs data analysis and visualization of historical stock market data.

    The script should be a Jupyter Notebook or a Python script that generates a detailed report.

    Functionality:
    1.  **Data Fetching**: Use the `yfinance` library to download historical stock data for a list of tickers (e.g., AAPL, MSFT, GOOG) over a specified date range (e.g., the last 5 years).
    2.  **Data Analysis with Pandas**:
        -   Calculate the daily percentage change in closing price.
        -   Calculate moving averages (e.g., 50-day and 200-day).
        -   Calculate the correlation between the returns of different stocks.
    3.  **Data Visualization with Matplotlib and Seaborn**:
        -   Plot the closing price over time for each stock.
        -   Plot the moving averages on the same chart as the closing price.
        -   Create a heatmap of the correlation matrix of the stocks' returns.
        -   Plot a histogram or a Kernel Density Estimate (KDE) plot of the daily returns for each stock.
    4.  **Reporting**: The script should be well-commented, with Markdown explanations for each step of the analysis and each visualization in the Jupyter Notebook. If it's a `.py` script, it should save the plots as image files.
    """,
    "15. Web Automation using Selenium": """
    Create a Python script that uses Selenium to automate a common web task: filling out an online form.

    Target Website: A practice form website like `https://www.scrapethissite.com/pages/forms/`.

    The script should:
    1.  **Use Selenium WebDriver**: Use `selenium` with `webdriver-manager` to automatically handle the browser driver.
    2.  **Load Data from CSV**: Create a CSV file (`data.csv`) with mock data (e.g., name, email, message). The script should read this data using Python's `csv` module.
    3.  **Automation Logic**:
        -   Open the target website.
        -   Loop through each row in the CSV file.
        -   For each row, locate the form fields (e.g., by name, ID, or XPath) and fill them with the corresponding data from the CSV.
        -   Use explicit waits (`WebDriverWait`) to ensure elements are present and clickable before interacting with them.
        -   Submit the form.
        -   After submitting, wait for a success message or a new page to load, take a screenshot, and save it with a unique name (e.g., `submission_1.png`).
    4.  **Headless Mode**: The script should be configurable to run in headless mode (without a visible browser window).
    5.  **Logging**: Log the script's progress, including which record it's currently processing and whether the submission was successful.
    """,
    "16. Audio Processing Script": """
    Create an advanced audio processing tool with a Python GUI (Tkinter).

    The tool should act as a simple audio file converter and manipulator.

    Libraries: `pydub`, `tkinter`

    Features:
    1.  **File Loading**: A button to load an audio file (supporting `.mp3`, `.wav`, `.ogg`).
    2.  **Format Conversion**: A dropdown menu allowing the user to select an output format (`.mp3`, `.wav`, `.flac`).
    3.  **Audio Slicing**: Input fields for a start time and end time (in seconds). The user can export only a specific slice of the audio file.
    4.  **Volume Control**: A slider to increase or decrease the volume of the audio file.
    5.  **Reverse Audio**: A button to reverse the audio.
    6.  **Export**: An "Export" button that applies all selected modifications (slicing, volume change, etc.) and saves the result as a new file in the chosen format.
    7.  **Progress Indicator**: Show a progress bar or a status message while processing and exporting the audio, especially for large files.
    """,
    "17. PDF Manipulation Script": """
    Generate a Python GUI application for common PDF manipulation tasks.

    GUI: PyQt6 or Tkinter
    Libraries: `PyPDF2` or `pymupdf`

    The application should be tab-based, with each tab performing a different function:
    1.  **Tab 1: Merge PDFs**:
        -   A listbox to display a list of PDF files added by the user.
        -   Buttons to "Add PDFs", "Remove Selected", and "Move Up/Down" to reorder the files.
        -   A "Merge" button that combines the PDFs in the specified order and saves the result as a new file.
    2.  **Tab 2: Split PDF**:
        -   A field to select a single PDF file.
        -   Input fields for a page range (e.g., "From page 5 to 10").
        -   A "Split" button that creates a new PDF containing only the specified pages.
    3.  **Tab 3: Watermark PDF**:
        -   A field to select the source PDF and another for the watermark PDF (a PDF containing the text or image to be used as a watermark).
        -   A "Watermark" button that overlays the watermark onto every page of the source PDF.
    """,
    "18. Network Scanner": """
    Create a command-line network scanning tool in Python.

    This tool will discover active hosts on a local network and scan for open ports on those hosts.

    Libraries: `scapy` for host discovery, `socket` for port scanning.

    Features:
    1.  **Host Discovery (Ping Scan)**:
        -   The tool should take a subnet as input (e.g., `192.168.1.0/24`).
        -   Use Scapy to send ARP requests to all possible IP addresses within that subnet.
        -   Listen for ARP replies to identify which hosts are online.
        -   Print a list of active IP addresses and their corresponding MAC addresses.
    2.  **Port Scanning**:
        -   After discovering hosts, the user can choose one of the active IPs to scan.
        -   The tool should then perform a TCP port scan on that host.
        -   The user can specify a range of ports to scan (e.g., 1-1024).
        -   Use multi-threading to speed up the port scanning process.
        -   For each port, the tool attempts to create a socket connection. If the connection is successful, the port is open.
        -   Display a list of open ports for the target IP.
    3.  **User Interface**: A clean, menu-driven command-line interface to choose between host discovery and port scanning.
    """,
    "19. QR Code Generator and Reader": """
    Build a two-part Python application with a GUI (Tkinter) for handling QR codes.

    Libraries: `qrcode` (with `pillow`) for generation, `opencv-python` and `pyzbar` for reading.

    The GUI should have two tabs:

    **Tab 1: QR Code Generator**
    1.  A text input field for the user to enter the data they want to encode (e.g., a URL, text, contact info).
    2.  Advanced options to customize the QR code: box size, border size, and fill/background color (using a color chooser).
    3.  A "Generate" button that displays the generated QR code in the GUI.
    4.  A "Save" button to save the generated QR code as an image file (`.png`).

    **Tab 2: QR Code Reader**
    1.  A button to "Scan from Webcam". This will open the computer's webcam feed in a new window using OpenCV.
    2.  The application should continuously scan the webcam feed for a QR code.
    3.  Once a QR code is detected, it should draw a bounding box around it on the video feed.
    4.  The decoded data from the QR code should be displayed in a text box on the GUI.
    5.  A button to "Scan from Image File" that lets the user select an image and decodes any QR code within it.
    """,
    "20. Basic Keylogger": """
    Generate a Python script for a basic, **educational-purpose** keylogger.

    **Disclaimer**: This script should only be used for educational purposes and on systems you own. Add a disclaimer in the code's comments and when the script is run.

    Library: `pynput`

    Features:
    1.  **Keystroke Logging**: The script should capture all keyboard presses. It needs to correctly handle special keys like Shift, Ctrl, Space, and Enter.
    2.  **Log File**: Log the keystrokes to a local text file (`keylog.txt`). The log should be human-readable, for example, printing `[SHIFT]` instead of a raw key code.
    3.  **Timed Reporting**: Instead of writing to the file after every keypress (which is inefficient), the script should store keystrokes in a memory buffer and write them to the log file periodically (e.g., every 60 seconds or after 100 keypresses).
    4.  **Stealth (Optional for education)**: The script should run in the background without a visible console window.
    5.  **Structured Code**: Use a class-based structure for the keylogger to manage its state (e.g., the buffer) and listeners neatly.
    """,
    "21. Simple Packet Sniffer": """
    Create a command-line packet sniffing tool in Python using the `scapy` library.

    The tool should be able to capture network packets and display relevant information about them.

    Features:
    1.  **Packet Capturing**:
        -   The user should be able to specify the network interface to sniff on. The script should be able to list available interfaces.
        -   The user can specify the number of packets to capture.
    2.  **Packet Filtering**:
        -   Allow the user to apply BPF (Berkeley Packet Filter) syntax to filter packets. For example, `tcp and port 80` to capture only HTTP traffic.
    3.  **Detailed Packet Analysis**:
        -   For each captured packet, the script should parse it and display a summary.
        -   The summary must include:
            -   Source and Destination IP addresses.
            -   Source and Destination Ports (if applicable, e.g., for TCP/UDP).
            -   The protocol (e.g., TCP, UDP, ICMP).
    4.  **Payload Display**:
        -   An option to display the raw payload of the packet in a hexadecimal and ASCII format.
    5.  **Save to PCAP**:
        -   Functionality to save the captured packets to a `.pcap` file, which can be opened later in tools like Wireshark.
    """,
    "22. Port Scanner with Banner Grabbing": """
    Create an advanced, multi-threaded port scanner in Python from scratch.

    The tool should be a command-line utility that takes a target IP address and a range of ports.

    Features:
    1.  **Multi-threading**: Use Python's `threading` module to scan multiple ports concurrently, significantly speeding up the process. Use a queue to manage the ports that need to be scanned by worker threads.
    2.  **Port Scanning**:
        -   Implement a TCP SYN scan (also known as a half-open scan) for stealthier scanning, using `scapy`. If that's too complex, a standard TCP connect scan using the `socket` library is acceptable.
        -   The user specifies the target IP and port range (e.g., `1-1000`).
    3.  **Banner Grabbing**:
        -   For every open port discovered, the script should attempt to connect and receive the first 1024 bytes of data.
        -   This data (the "banner") can often identify the service running on that port (e.g., "SSH-2.0-OpenSSH_8.2p1").
        -   The received banner should be printed next to the open port number.
    4.  **Output**: The final output should be a clean list of all open ports, the common name of the service on that port (if known), and the grabbed banner.
    """,
    "23. DNS Lookup Tool": """
    Build a command-line DNS lookup tool in Python, similar to `nslookup` or `dig`.

    Library: `dnspython`

    Features:
    1.  **Record Types**: The tool must be able to query for multiple common DNS record types, including:
        -   A (IPv4 Address)
        -   AAAA (IPv6 Address)
        -   MX (Mail Exchange)
        -   NS (Name Server)
        -   CNAME (Canonical Name)
        -   TXT (Text Record)
    2.  **Command-Line Interface**: Use the `argparse` module to create a professional command-line interface. The user should be able to specify the domain to query and the record type.
        -   Example usage: `python dns_tool.py google.com --type A`
        -   Example usage: `python dns_tool.py gmail.com --type MX`
    3.  **Specify DNS Server**: An optional argument to specify a particular DNS server to use for the query (e.g., `--server 8.8.8.8`). If not provided, it should use the system's default resolver.
    4.  **Formatted Output**: Display the results in a clean, human-readable format, clearly labeling the question and the answer sections, including the record type, TTL, and the record data.
    """,
    "24. Reverse Image Search Tool": """
    Create a Python script that performs a reverse image search using Google Images.

    This script will automate the process of uploading an image and finding visually similar results.

    Libraries: `selenium`, `webdriver-manager`

    Functionality:
    1.  **Input**: The script should accept the path to a local image file as a command-line argument.
    2.  **Automation with Selenium**:
        -   The script launches a web browser (in headless mode to be discreet).
        -   Navigates to `images.google.com`.
        -   It must correctly handle clicking the "Search by image" (camera) icon.
        -   It then interacts with the "Upload a file" dialog to provide the path to the local image. This requires using `element.send_keys()` on the hidden file input element.
    3.  **Scraping Results**:
        -   After the image is uploaded and search results are displayed, the script needs to parse the resulting page.
        -   It should find and extract the "Possible related search" text that Google provides.
        -   It should also find and extract the URLs of the top 5 visually similar images.
    4.  **Output**: The script should print the "Possible related search" text and the list of URLs for the visually similar images to the console.
    """,
    "25. Text Summarization Tool": """
    Generate an advanced Text Summarization Tool in Python. The tool should have a graphical user interface (GUI) built with **Tkinter** or **PyQt6**.

    **Features**:
    1.  A text area to paste the article or long text.
    2.  An option to upload a text file (`.txt`, `.pdf`, `.docx`). Use libraries like `PyPDF2` and `python-docx` for file handling.
    3.  A slider or input field to control the summary length (e.g., as a percentage of the original text).
    4.  Implement two different summarization techniques:
        a.  **Extractive Summarization**: Use libraries like **spaCy** or **NLTK** to rank sentences based on word frequency (TF-IDF) and select the most important ones.
        b.  **Abstractive Summarization**: Integrate a pre-trained transformer model like **T5** or **BART** from the **Hugging Face Transformers** library.
    5.  A button or radio buttons to switch between Extractive and Abstractive methods.
    6.  A display area to show the generated summary.
    7.  A 'Copy to Clipboard' button for the summary.
    8.  Include robust error handling for invalid file formats or empty input.
    The code should be well-structured, with classes for the GUI and the summarization logic, and include detailed comments.
    """,
    "26. Sentiment Analysis Tool": """
    Create a GUI application for performing sentiment analysis on text.

    GUI: **PyQt6**
    Libraries: **NLTK** or **TextBlob** for simple analysis, and **Hugging Face Transformers** for advanced analysis.

    Features:
    1.  **Input**: A large text box for the user to paste text (e.g., a product review, a tweet).
    2.  **Analysis Models**: Allow the user to choose between two models via radio buttons:
        -   **Simple Model**: Use TextBlob's built-in sentiment analysis, which provides polarity (negative/positive) and subjectivity scores.
        -   **Advanced Model**: Use a pre-trained sentiment analysis model from Hugging Face (e.g., `distilbert-base-uncased-finetuned-sst-2-english`) for more accurate results.
    3.  **Analysis Button**: A button to trigger the analysis.
    4.  **Output Display**:
        -   Display the sentiment (Positive, Negative, Neutral).
        -   Show a confidence score or polarity score.
        -   Use a color-coded background for the result (e.g., green for positive, red for negative).
    5.  **Batch Analysis**: An option to upload a CSV file with a 'text' column and perform sentiment analysis on each row, saving the results back to a new CSV file.
    """,
    "27. Spam Email Filter": """
    Build and train a machine learning model to act as a spam email filter.

    This project is a command-line or Jupyter Notebook-based data science project.

    Libraries: `pandas`, `scikit-learn`, `nltk`

    Steps:
    1.  **Dataset**: Use a well-known public dataset of emails labeled as spam or ham (not spam), like the "SMS Spam Collection Data Set" from the UCI Machine Learning Repository.
    2.  **Data Preprocessing**:
        -   Load the data using pandas.
        -   Clean the text data: convert to lowercase, remove punctuation, and remove stop words using NLTK.
        -   Perform lemmatization or stemming on the words.
    3.  **Feature Extraction**:
        -   Convert the cleaned text data into numerical vectors using the TF-IDF (Term Frequency-Inverse Document Frequency) vectorization technique from scikit-learn.
    4.  **Model Training**:
        -   Split the dataset into training and testing sets.
        -   Train a classification model, such as **Naive Bayes** (which is particularly effective for this task), Logistic Regression, or a Support Vector Machine (SVM).
    5.  **Evaluation**:
        -   Evaluate the model's performance on the test set.
        -   Print a classification report showing precision, recall, and F1-score.
        -   Display the confusion matrix.
    6.  **Prediction Function**: Create a function that takes a new email text as input and predicts whether it is spam or ham.
    """,
    "28. Plagiarism Checker": """
    Create a functional Plagiarism Checker tool.

    This tool will compare two text documents and calculate a similarity score.

    GUI (Tkinter):
    1.  Two large text areas, side-by-side, for the user to paste the two texts they want to compare.
    2.  Buttons above each text area to "Load from File" (`.txt`, `.docx`).
    3.  **Comparison Logic**:
        -   Implement at least two methods for comparison:
            a.  **Vector-based Similarity**: Use `scikit-learn` to convert both texts into TF-IDF vectors. Then, calculate the **cosine similarity** between the two vectors. This gives a score from 0 to 1.
            b.  **Sequence-based Similarity**: Use Python's `difflib.SequenceMatcher` to find the longest contiguous matching blocks and calculate a similarity ratio.
    4.  **Run Check Button**: A button that, when clicked, performs the comparison using both methods.
    5.  **Results Display**:
        -   Display the similarity scores from both methods (e.g., "Cosine Similarity: 0.85", "Sequence Similarity: 0.78").
        -   Optionally, highlight the matching sentences or phrases in both text boxes.
    """,
    "29. Fake News Detector": """
    Develop a machine learning model to detect fake news. This is a data science project best presented in a Jupyter Notebook.

    Libraries: `pandas`, `numpy`, `scikit-learn`, `nltk`

    Project Workflow:
    1.  **Dataset**: Use a public dataset for fake news detection, such as the one from Kaggle (often containing a 'title', 'text', and 'label' column).
    2.  **Exploratory Data Analysis (EDA)**:
        -   Analyze the dataset to understand its structure.
        -   Visualize the distribution of real vs. fake news labels.
        -   Analyze word clouds for both categories to see common terms.
    3.  **Text Preprocessing**:
        -   Combine the title and the text for a richer feature set.
        -   Perform standard text cleaning: lowercase, remove punctuation, remove stop words.
    4.  **Feature Engineering**:
        -   Use `TfidfVectorizer` from `scikit-learn` to convert the text data into a matrix of TF-IDF features.
    5.  **Model Training**:
        -   Split the data into training and testing sets.
        -   Train a `PassiveAggressiveClassifier` from `scikit-learn`, which is known to work well for this text classification task.
    6.  **Model Evaluation**:
        -   Make predictions on the test set.
        -   Print the accuracy score and a detailed confusion matrix to see how many fake/real news articles were classified correctly.
    7.  **Prediction Pipeline**: Save the trained model and the vectorizer so you can build a simple function that takes a new news article text and predicts its authenticity.
    """,
    "30. Website Vulnerability Scanner": """
    Create a command-line tool that performs basic vulnerability scanning on a given website URL.

    **Disclaimer**: This tool should only be used on websites you own or have explicit permission to scan.

    Libraries: `requests`, `BeautifulSoup4`

    Features:
    1.  **Input**: The tool takes a base URL as input from the command line.
    2.  **Spider/Crawler**:
        -   The script must first crawl the website to discover all unique links and forms within the same domain. It should maintain a list of visited URLs to avoid infinite loops.
    3.  **Vulnerability Checks**: For each discovered URL and form, it should perform the following checks:
        a.  **SQL Injection Scan**: For every form, submit the form with classic SQL injection payloads (like `' OR 1=1 --`) in each input field. Check if the response contains common SQL error messages.
        b.  **Cross-Site Scripting (XSS) Scan**:
            -   **Reflected XSS**: Submit forms and URL parameters with a simple XSS payload (e.g., `<script>alert('xss')</script>`). Then, check if the payload is reflected back in the HTML response.
        c.  **Directory Traversal Scan**: Attempt to access sensitive files by appending payloads like `../../../../etc/passwd` to the URL. Check for unusual responses.
    4.  **Reporting**:
        -   The tool should log its progress in real-time.
        -   At the end of the scan, it must generate a clean report listing all the potential vulnerabilities found, including the URL, the parameter, and the type of vulnerability discovered.
    """,
    "31. AI-Powered Recipe Generator": """
    Create an AI-Powered Recipe Generator with a GUI (Tkinter or PyQt6).

    This tool will generate new recipes based on ingredients the user has.

    Features:
    1.  **GUI**:
        -   A text input field where the user can list ingredients they have, separated by commas (e.g., "chicken, rice, tomatoes, garlic").
        -   A dropdown menu for selecting the course (e.g., 'Appetizer', 'Main Course', 'Dessert').
        -   A "Generate Recipe" button.
        -   A large, styled text area to display the generated recipe, including a title, ingredients list, and step-by-step instructions.
    2.  **AI Integration**:
        -   Use a generative AI API (like Google's Gemini API) to generate the recipes.
        -   The script will construct a detailed prompt for the AI based on the user's input. For example: "You are a professional chef. Create a recipe for a [course] using the following ingredients: [user's ingredients]. Provide a creative title, a formatted list of all necessary ingredients, and clear, step-by-step instructions."
    3.  **API Key Management**: A simple settings dialog where the user can securely enter and save their AI API key.
    4.  **Save/Export**: A button to save the generated recipe as a `.txt` or `.md` file.
    """,
    "32. Real-time Stock Market Dashboard": """
    Build a real-time stock market dashboard using Python's Dash framework.

    This web-based dashboard will continuously update with the latest stock prices.

    Libraries: `dash`, `dash_core_components`, `dash_html_components`, `yfinance`, `pandas`

    Features:
    1.  **Web Interface**: A clean dashboard layout with a title and multiple components.
    2.  **User Input**: An input box where the user can enter multiple stock tickers (e.g., "AAPL, TSLA, NVDA").
    3.  **Live Price Updates**:
        -   The dashboard should have a graph that plots the stock price for the selected tickers over the current day.
        -   Use a `dcc.Interval` component to trigger an update every 60 seconds.
        -   The update callback will re-fetch the latest stock data using `yfinance` and update the graph.
    4.  **Data Table**: Display a table below the graph showing key metrics for the selected stocks: current price, previous close, day's high/low, and volume. This table should also update in real-time.
    5.  **Candlestick Chart**: Include a candlestick chart showing the Open, High, Low, Close (OHLC) data for the selected period.
    """,
    "33. Discord/Telegram Bot with Moderation Features": """
    Create a multi-functional bot for Discord or Telegram.

    Target Platform: Discord (using `discord.py`) or Telegram (using `python-telegram-bot`).

    Features:
    1.  **Basic Commands**:
        -   `!hello`: The bot responds with a greeting.
        -   `!ping`: The bot replies with "Pong!" and its current latency.
    2.  **Moderation Tools**:
        -   `!kick [user] [reason]`: Kicks a user from the server (requires admin privileges).
        -   `!ban [user] [reason]`: Bans a user.
        -   `!mute [user] [duration]`: Mutes a user for a specified duration (e.g., "10m" for 10 minutes).
        -   `!clear [amount]`: Deletes a specified number of messages from the channel.
    3.  **Role Management**: `!addrole [user] [role]` and `!removerole [user] [role]` commands.
    4.  **Logging**: Create a dedicated private channel where the bot logs all moderation actions (who was kicked/banned, by which moderator, and for what reason).
    5.  **Error Handling**: The bot should provide helpful feedback if a command is used incorrectly or if it lacks the necessary permissions.
    """,
    "34. API for a Simple Blog": """
    Develop a RESTful API for a simple blog using Python's FastAPI framework.

    This API will provide endpoints to manage blog posts.

    Libraries: `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`

    Features:
    1.  **Data Model**: Use Pydantic to define the schema for a `Post` (id, title, content, author).
    2.  **Database**: Use SQLAlchemy with a SQLite database to store the posts.
    3.  **CRUD Endpoints**: Implement the following RESTful endpoints:
        -   `POST /posts/`: Create a new post.
        -   `GET /posts/`: Retrieve a list of all posts.
        -   `GET /posts/{post_id}`: Retrieve a single post by its ID.
        -   `PUT /posts/{post_id}`: Update an existing post.
        -   `DELETE /posts/{post_id}`: Delete a post.
    4.  **API Documentation**: FastAPI will automatically generate interactive API documentation (using Swagger UI and ReDoc), which should be accessible at `/docs` and `/redoc`.
    5.  **Error Handling**: Implement proper HTTP status codes and error responses for cases like a post not being found (404).
    """,
    "35. Video Downloader for YouTube": """
    Create a GUI-based YouTube video downloader.

    Libraries: `pytube`, `tkinter`

    GUI Features:
    1.  **URL Input**: A text field to paste the YouTube video URL.
    2.  **Fetch Streams**: A "Get Video Info" button that uses `pytube` to fetch all available video and audio streams for the given URL.
    3.  **Stream Selection**: Display the available streams in a dropdown menu or a listbox. The display should be user-friendly, showing resolution, file type, and file size (e.g., "Video - 720p - mp4 - 54.3 MB").
    4.  **Download Location**: A button to let the user choose a directory where the downloaded file will be saved.
    5.  **Download Button**: A "Download" button that starts the download process for the selected stream.
    6.  **Progress Bar**: A progress bar that visually represents the download progress in real-time. `pytube` provides a callback for this.
    7.  **Status Label**: A label to show the current status (e.g., "Downloading...", "Download Complete", or any errors).
    """,
    "36. Personalized News Aggregator": """
    Build a personalized news aggregator that fetches news based on user-defined keywords and presents it in a clean web interface.

    Backend: Flask or FastAPI
    Frontend: HTML/CSS (using Jinja2 templates)
    API: Use a free news API like NewsAPI.org.

    Features:
    1.  **Keyword Management**: A settings page where the user can add and remove keywords they are interested in (e.g., "Python", "space exploration", "AI ethics").
    2.  **Automated Fetching**: A background script (could be a scheduled job) that periodically fetches the latest news articles for all user-defined keywords from the NewsAPI.
    3.  **Database Storage**: Store the fetched articles (title, source, description, URL) in a SQLite database to avoid duplicates and build a historical archive.
    4.  **Web Interface**:
        -   A main page that displays a feed of all aggregated news, sorted by publication date.
        -   The user should be able to filter the news by their saved keywords.
    5.  **User Authentication**: (Optional advanced feature) Add a simple user login system so that multiple users can have their own personalized keyword lists.
    """,
    "37. GUI Database Client": """
    Create a general-purpose GUI database client for SQLite databases.

    Framework: PyQt6

    Features:
    1.  **Connection**: A menu option to "Open Database" which allows the user to select a `.db` or `.sqlite` file.
    2.  **Schema Viewer**: A tree view panel on the left that displays the database schema: tables, and for each table, its columns and their data types.
    3.  **Data Viewer**: When a user clicks on a table in the schema viewer, the main area of the window should display the table's data in a tabular format (using `QTableView`).
    4.  **SQL Query Executor**:
        -   A text editor area where the user can write and execute custom SQL queries.
        -   A "Run Query" button.
        -   The results of `SELECT` queries should be displayed in the data view table.
        -   For `INSERT`, `UPDATE`, `DELETE` queries, a message should be displayed indicating success or failure and the number of rows affected.
    5.  **Data Editing**: Allow users to edit data directly in the table view. Changes should be committable to the database with a "Save Changes" button.
    """,
    "38. Code Plagiarism Checker": """
    Develop an advanced Code Plagiarism Checker that can compare a source code file against a directory of other files.

    This is a command-line tool.

    Features:
    1.  **Language Parsing**:
        -   The tool should first parse the source code to remove non-essential elements like comments and whitespace.
        -   It should then convert the code into a sequence of tokens or an Abstract Syntax Tree (AST) using Python's `ast` module. This is more effective than simple text comparison.
    2.  **Comparison Algorithm**:
        -   Compare the AST of the source file against the AST of every file in the target directory.
        -   Implement a structural similarity algorithm to find how similar the code structures are, not just the variable names. A simple approach is to compare the sequence of node types in the AST.
    3.  **Input**:
        -   The tool takes two arguments: the path to the source file and the path to the directory of files to check against.
    4.  **Reporting**:
        -   The tool should output a report listing the top 5 most similar files from the directory, along with their calculated similarity score (as a percentage).
        -   Example output:
            ```
            Checking 'source.py' against 50 files in 'submissions/'...

            Top 5 Most Similar Files:
            1. submissions/user34.py - 95% similarity
            2. submissions/user12.py - 92% similarity
            ...
            ```
    """,
    "39. Workout Tracker and Planner": """
    Create a GUI application for tracking workouts and planning fitness routines.

    GUI: Tkinter or PyQt6
    Database: SQLite

    Features:
    1.  **Exercise Database**:
        -   A pre-populated, editable database of exercises, categorized by muscle group (e.g., 'Chest', 'Back', 'Legs') and type (e.g., 'Barbell', 'Dumbbell', 'Bodyweight').
    2.  **Workout Logging**:
        -   A section to log a workout session. The user selects a date, chooses an exercise from the database, and enters the details (e.g., sets, reps, weight).
        -   The UI should allow adding multiple exercises to a single session.
    3.  **Routine Planner**:
        -   Users can create workout routines (e.g., "Push Day", "Leg Day").
        -   A routine consists of a list of exercises.
        -   When logging a new workout, the user can select a routine to pre-fill the exercise list.
    4.  **Progress Visualization**:
        -   A "Progress" tab where the user can select an exercise and see a chart (using Matplotlib) of their performance over time (e.g., plotting the maximum weight lifted for that exercise over the last 3 months).
    """,
    "40. Job Application Bot": """
    Create a web automation bot that automatically applies to jobs on a platform like LinkedIn or Indeed.

    **Disclaimer**: Use this responsibly and be aware of website terms of service. This is for educational demonstration.

    Libraries: `selenium`, `webdriver-manager`

    Functionality:
    1.  **Configuration**: A configuration file (`config.json`) to store user credentials (email/password), job search keywords (e.g., "Python Developer"), location, and the path to the user's resume file.
    2.  **Login**: The bot first logs into the job platform using the provided credentials.
    3.  **Job Search**: It navigates to the jobs section, enters the search keywords and location, and applies relevant filters (e.g., "Easy Apply" on LinkedIn).
    4.  **Application Logic**:
        -   The bot iterates through the search results.
        -   For each job, it clicks the "Easy Apply" or similar button.
        -   It intelligently fills out the application form, uploading the resume and answering simple questions based on pre-defined rules in the config.
        -   Use explicit waits to handle dynamic page loads.
    5.  **Tracking**: The bot should log every job it applies to in a CSV file, including the job title, company, and a direct link to the posting, to avoid duplicate applications.
    """,
    "41. Smart Home Automation Script": """
    Create a central Python script to control various smart home devices from different brands.

    This script will act as a bridge, controlled by a simple Flask web interface.

    Integrations (choose at least two):
    -   Philips Hue (using the `phue` library) for smart lights.
    -   TP-Link Kasa (using `pykasa`) for smart plugs.
    -   A generic MQTT broker for DIY devices.

    Features:
    1.  **Flask Web UI**: A simple, mobile-friendly web dashboard with buttons to control devices.
        -   Toggle buttons for individual lights and plugs.
        -   A "Scene" button, like "Movie Mode," which turns some lights off and dims others.
    2.  **Device Abstraction**: Create a unified class structure. For example, a `Light` class and a `Plug` class. The implementation details for Hue or Kasa should be hidden behind a common interface (e.g., `light.turn_on()`).
    3.  **Discovery**: A function that can scan the local network to discover new Hue bridges or Kasa devices.
    4.  **Scheduling**: Allow users to set simple schedules via the web UI, e.g., "Turn on the living room lamp at 7 PM every day." Use a library like `schedule` to run these tasks.
    """,
    "42. Music Genre Classification from Audio": """
    Develop a machine learning project to classify the genre of a music file.

    This is a data science project suitable for a Jupyter Notebook.

    Libraries: `librosa` (for audio feature extraction), `pandas`, `scikit-learn`

    Workflow:
    1.  **Dataset**: Use the GTZAN Genre Collection dataset, which contains 1000 audio files across 10 genres.
    2.  **Feature Extraction**:
        -   For each audio file, use `librosa` to extract key features. This is the most crucial step.
        -   Extract features like: MFCCs (Mel-Frequency Cepstral Coefficients), Chroma, Spectral Contrast, and Zero-Crossing Rate.
        -   Aggregate these features (e.g., by taking the mean) for each file and store them in a CSV with their corresponding genre label.
    3.  **Model Training**:
        -   Load the feature data from the CSV using pandas.
        -   Split the data into training and testing sets.
        -   Train a robust classification model like a Support Vector Machine (SVM) or a Gradient Boosting Classifier.
    4.  **Evaluation**:
        -   Evaluate the model's accuracy on the test set.
        -   Display a classification report and a confusion matrix to see which genres are often confused.
    5.  **Prediction Pipeline**: Create a function that takes a new audio file path, extracts its features using the same process, and predicts its genre.
    """,
    "43. Language Learning Flashcard App": """
    Create a GUI-based language learning flashcard application.

    GUI: PyQt6 or Tkinter
    Database: SQLite

    Features:
    1.  **Deck Management**:
        -   Users can create different "decks" of flashcards (e.g., "Spanish Vocabulary," "French Verbs").
        -   The main window shows a list of all decks.
    2.  **Card Creation**: Inside a deck, users can add new cards. Each card has a "Front" (with the word in the native language) and a "Back" (with the translation).
    3.  **Study Mode**:
        -   When a user starts a study session for a deck, the app displays the front of a card.
        -   After the user thinks of the answer, they click a "Show Answer" button.
        -   The app then reveals the back of the card and asks the user to self-assess their performance with buttons like "Easy," "Good," or "Again."
    4.  **Spaced Repetition System (SRS)**:
        -   Implement a basic SRS algorithm (like a simplified Anki model).
        -   Based on the user's self-assessment, the app schedules the next time that card will be shown. "Again" shows it soon, while "Easy" shows it much later.
        -   The study session should prioritize cards that are due to be reviewed.
    """,
    "44. E-book Reader and Manager": """
    Build a desktop e-book reader and library management application.

    GUI: PyQt6
    Libraries: `PyMuPDF` (for `.pdf` and `.epub`), `beautifulsoup4` (for parsing epub content).

    Features:
    1.  **Library View**:
        -   A main window that displays a grid or list of all e-book covers in the user's library.
        -   A button to "Import E-book" which copies a supported file into the application's library folder.
    2.  **Metadata Extraction**: When importing, the app should extract metadata like the title, author, and cover image from the e-book file and store it in a SQLite database.
    3.  **Reader View**:
        -   When an e-book is opened, a new window appears.
        -   It should display the book's content page by page.
        -   "Next Page" and "Previous Page" buttons.
        -   The application must remember the user's last-read page for each book.
    4.  **Customization**: Options to change the font size and switch between a day (white background) and night (dark background) reading mode.
    """,
    "45. Markdown to HTML Converter with Live Preview": """
    Create a simple Markdown editor with a live HTML preview.

    GUI: PyQt6
    Libraries: `markdown2`

    Features:
    1.  **Split-Pane Interface**: The main window should be split into two vertical panes.
    2.  **Left Pane: Markdown Editor**:
        -   A text editor widget where the user can type Markdown.
    3.  **Right Pane: HTML Preview**:
        -   A web view widget (`QWebEngineView`) that displays the rendered HTML.
    4.  **Live Update**:
        -   As the user types in the Markdown editor, the application should automatically convert the Markdown to HTML in real-time.
        -   The HTML preview pane should update instantly to reflect the changes. This is achieved by connecting a "text changed" signal from the editor to a function that performs the conversion and updates the preview.
    5.  **File Operations**: Basic menu options to "Open" a `.md` file and "Save" the content of the editor. An "Export to HTML" option is also required.
    """,
    "46. Website Health Checker": """
    Build a tool that monitors a list of websites for uptime and broken links.

    This can be a command-line tool or have a simple Flask web dashboard.

    Features:
    1.  **Configuration**: A JSON or YAML file where the user lists the websites they want to monitor.
    2.  **Uptime Check**:
        -   The script periodically (e.g., every 5 minutes) sends an HTTP GET request to each website's homepage.
        -   It checks the HTTP status code. If it's not in the 200-299 range, the website is considered "down."
    3.  **Broken Link Crawler**:
        -   Once per day, the script performs a deeper check. It crawls each website, finding all internal links.
        -   For each discovered internal link, it sends a HEAD request to check its status code.
        -   It compiles a list of all links that return a 4xx (client error) or 5xx (server error) status code.
    4.  **Notifications**:
        -   If a website goes down, or if new broken links are found, the tool sends a notification.
        -   Implement at least one notification method: email (`smtplib`) or a push notification service like Pushbullet.
    5.  **Dashboard/Report**: A simple web dashboard (Flask) or a daily email report that summarizes the status of all monitored websites and lists any found issues.
    """,
    "47. AI Story Generator": """
    Create an AI-powered collaborative story generator.

    This application will have a GUI (Tkinter or PyQt6) where a user and an AI take turns writing a story.

    Features:
    1.  **GUI**:
        -   A large text area to display the story as it's being written.
        -   An input field for the user to write their part of the story (e.g., a sentence or a paragraph).
        -   A "Take Turn" button.
    2.  **Story Flow**:
        -   The user starts by writing an opening sentence or two.
        -   When they click "Take Turn," their text is added to the main story.
        -   The application then sends the entire story so far to a generative AI (like Google's Gemini).
        -   The prompt should instruct the AI to continue the story, adding the next paragraph.
    3.  **AI Integration**:
        -   The AI's response is then appended to the main story text area.
        -   The user can then write their next turn, and the cycle continues.
    4.  **Customization**: Options to set the genre of the story (e.g., 'Fantasy', 'Sci-Fi', 'Mystery'), which will be included in the prompt to the AI to guide its responses.
    5.  **Save Story**: A button to save the complete collaborative story to a text file.
    """,
    "48. Sudoku Solver with a GUI": """
    Build a Sudoku solver that has a graphical interface for user interaction.

    GUI: Pygame or Tkinter

    Features:
    1.  **Sudoku Grid**:
        -   A 9x9 grid of input boxes where the user can enter the numbers of a Sudoku puzzle.
        -   The GUI should visually distinguish the 3x3 subgrids.
    2.  **Input Validation**: As the user types, the application should validate the input (only numbers 1-9 are allowed).
    3.  **Solving Algorithm**:
        -   Implement the **backtracking algorithm** to solve the Sudoku puzzle. This is a classic recursive algorithm perfect for this problem.
    4.  **"Solve" Button**:
        -   When clicked, the script runs the backtracking algorithm on the puzzle entered by the user.
        -   The solution should then be displayed on the grid.
    5.  **Visualization (Optional)**:
        -   An option to "Visualize" the solving process. This would run the algorithm more slowly, updating the GUI to show how the backtracking works—filling in numbers and erasing them when a dead end is hit. This is an excellent way to demonstrate the algorithm.
    6.  **"Clear" Button**: A button to clear the entire grid.
    """,
    "49. Lyrics Fetcher with Music Player Integration": """
    Create a tool that automatically fetches the lyrics for the song currently playing on the user's computer.

    This script will run in the background.

    Integration:
    -   **Spotify**: Use the Spotify API (via `spotipy`) to get the currently playing track's title and artist. This requires the user to authenticate.

    Lyrics Fetching:
    -   Use a lyrics API or scrape a lyrics website (e.g., Genius) to find the lyrics for the song. The `lyricsgenius` library is excellent for this.

    GUI (Tkinter):
    1.  A simple, small window that always stays on top.
    2.  **Authentication**: On first run, it should guide the user through the Spotify and Genius API authentication process.
    3.  **Display**: The window should display the lyrics of the currently playing song.
    4.  **Auto-Update**: The script should poll Spotify every few seconds. If the song changes, it should automatically fetch the new lyrics and update the display.
    5.  **Status**: A small status bar indicating the current song or if no song is playing.
    """,
    "50. GUI Regex Tester": """
    Build a real-time Regular Expression (Regex) testing tool with a GUI.

    GUI: PyQt6

    Features:
    1.  **Three Main Text Boxes**:
        -   **Regex Pattern**: An input field for the user to type their regex pattern.
        -   **Test String**: A large text area for the user to paste the text they want to test the pattern against.
        -   **Match Results**: A read-only text area to display the results.
    2.  **Real-time Highlighting**:
        -   As the user types their regex pattern or modifies the test string, all substrings in the test string that match the pattern should be highlighted in real-time.
    3.  **Match Information**:
        -   The "Match Results" box should list all the matches found.
        -   If the regex contains capturing groups, the results should clearly show the full match and the contents of each group for every match.
    4.  **Regex Flags**: Checkboxes to enable common regex flags like "Ignore Case" (`re.IGNORECASE`), "Multiline" (`re.MULTILINE`), and "Dot All" (`re.DOTALL`).
    5.  **Regex Cheat Sheet**: A "Help" menu with a quick reference or cheat sheet for common regex syntax.
    """,
    "51. Multi-threaded Web Crawler": """
    Create a high-performance, multi-threaded web crawler in Python.

    This is a command-line tool designed for speed.

    Libraries: `requests`, `BeautifulSoup4`, `threading`, `queue`

    Features:
    1.  **Seed URL**: The script starts with a single "seed" URL and a domain to constrain the crawl (to prevent it from crawling the entire internet).
    2.  **Thread-Safe Queue**: Use Python's `queue.Queue` to hold the URLs that need to be crawled. This is naturally thread-safe.
    3.  **Worker Threads**:
        -   The user can specify the number of worker threads to use.
        -   Each thread runs a function that:
            a.  Pulls a URL from the queue.
            b.  Fetches the HTML content of the URL.
            c.  Parses the HTML with BeautifulSoup to find all `<a>` tags.
            d.  For each new link found, if it's within the target domain and hasn't been seen before, it's added to the queue and a global set of visited URLs.
    4.  **Output**: The crawler should print the URLs as it discovers them and, at the end, output a summary (e.g., "Crawled 1500 pages with 10 threads in 45 seconds.")
    5.  **Error Handling**: Must gracefully handle network errors, timeouts, and non-HTML content.
    """
}

def main():
    """The main function to run the project prompt generator."""
    while True:
        clear_console()
        print("--- Python Project Prompt Generator ---")
        print("Choose a project to get the detailed prompt for your AI code generator.\n")

        # Storing keys to map integer input to the dictionary key
        project_keys = list(projects.keys())
        for i, title in enumerate(project_keys):
            print(f"{i + 1}. {title.split('. ')[1]}") # Print without the original number

        print("\n-------------------------------------------")
        choice = input("Choose a project number to get the prompt (or 'q' to quit): ")

        if choice.lower() == 'q':
            break

        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(project_keys):
                chosen_key = project_keys[choice_index]
                prompt = projects[chosen_key]

                clear_console()
                print("--- Prompt for: " + chosen_key.split('. ')[1] + " ---")
                print("\nCopy the entire text below and paste it into your AI model.\n")
                print("="*60)
                # Use textwrap to format the prompt nicely
                print(textwrap.dedent(prompt).strip())
                print("="*60)

                input("\nPress Enter to return to the project list...")
            else:
                input(f"\nInvalid number. Please choose a number between 1 and {len(project_keys)}. Press Enter to try again.")
        except ValueError:
            input("\nInvalid input. Please enter a number or 'q'. Press Enter to try again.")

if __name__ == "__main__":
    main()
