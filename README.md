## Installation

# 1. Clone the repository
git clone https://github.com/yourusername/ai-password-cracker.git

cd ai-password-cracker

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

## How to Use
# Run the tool
python app/gui_cracker.py

## Inside the GUI:
1. Enter target login URL (e.g. from OWASP Juice Shop)

2. Input target username/email

3. Choose a wordlist or select brute-force mode

4. Choose attack type:

- Dictionary

- Brute Force (All)

- Brute Force (AI Filtered)

- AI Prediction Only

5. Click "Start Cracking" and monitor the logs.
