import os
import csv
import glob
from datetime import datetime
import shutil

# Configuration
MEMO_DIR = "memos/trades"
ARCHIVE_DIR = "memos/archive"
PORTFOLIO_FILE = "data/portfolio/trades.csv"

def execute_trades():
    print("--- 🚀 Executing Approved Trades ---")
    
    # Ensure directories exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    
    # Get all memos for today (or all present in the folder)
    memos = glob.glob(f"{MEMO_DIR}/*.md")
    
    if not memos:
        print("No trade memos found to execute.")
        return

    # Prepare CSV Header if new file
    file_exists = os.path.exists(PORTFOLIO_FILE)
    
    with open(PORTFOLIO_FILE, 'a', newline='') as csvfile:
        fieldnames = ['Date', 'Ticker', 'Action', 'Type', 'Strike', 'Expiry', 'Price', 'Quantity', 'Cost', 'Status', 'Memo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        total_cost = 0.0
        
        for memo_path in memos:
            try:
                with open(memo_path, 'r') as f:
                    content = f.read()
                    
                # Parse Memo (Simple Parsing based on known format)
                # We should probably have a structured way, but parsing text is fine for now
                lines = content.split('\n')
                data = {'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Status': 'FILLED', 'Memo': os.path.basename(memo_path)}
                
                for line in lines:
                    if "**Signal**" in line:
                        # Extract signal? Not strictly needed for ledger
                        pass
                    if "*   **Direction**" in line:
                        data['Action'] = line.split(":")[1].strip().split(' ')[0] # SELL
                        data['Type'] = 'PUT' if 'PUT' in line else 'CALL'
                    if "*   **Contract**" in line:
                        # Format: 2025-11-28 $100.0 PUT
                        parts = line.split(":")[1].strip().split(' ')
                        data['Expiry'] = parts[0]
                        data['Strike'] = parts[1].replace('$', '')
                    if "*   **Price**" in line:
                        data['Price'] = float(line.split("$")[1].strip())
                    if "*   **Position Size**" in line:
                        data['Quantity'] = int(line.split(":")[1].strip().split(' ')[0])
                    if "*   **Total Risk**" in line:
                        data['Cost'] = float(line.split("$")[1].strip())
                        
                # Fallback for Ticker (from filename)
                # 2025-11-21_HOOD_SELL.md
                filename = os.path.basename(memo_path)
                data['Ticker'] = filename.split('_')[1]
                
                # Write to Ledger
                writer.writerow(data)
                print(f"✅ FILLED: {data['Action']} {data['Quantity']}x {data['Ticker']} {data['Type']} ${data['Strike']} @ ${data['Price']} (Cost: ${data['Cost']})")
                
                total_cost += data.get('Cost', 0)
                
                # Archive Memo
                shutil.move(memo_path, os.path.join(ARCHIVE_DIR, filename))
                
            except Exception as e:
                print(f"❌ Failed to execute {memo_path}: {e}")

    print("-" * 40)
    print(f"💰 Total Capital Deployed: ${total_cost:.2f}")
    print(f"📂 Trades logged to {PORTFOLIO_FILE}")
    print(f"🗄  Memos archived to {ARCHIVE_DIR}")

if __name__ == "__main__":
    execute_trades()
