import os
import glob

MEMO_DIR = "memos/trades"

def approve_memos():
    memos = glob.glob(f"{MEMO_DIR}/*.md")
    print(f"Found {len(memos)} memos to approve.")
    
    for memo_path in memos:
        with open(memo_path, 'r') as f:
            content = f.read()
            
        # 1. Update Status
        content = content.replace("Status: 🟡 PENDING REVIEW", "Status: 🟢 APPROVED")
        
        # 2. Check Box
        content = content.replace("- [ ] **APPROVED**", "- [x] **APPROVED**")
        
        with open(memo_path, 'w') as f:
            f.write(content)
            
        print(f"✅ Marked as APPROVED: {os.path.basename(memo_path)}")

if __name__ == "__main__":
    approve_memos()
