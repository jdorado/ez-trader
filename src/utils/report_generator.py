import os
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    """Generates markdown reports for trading activities."""
    
    def __init__(self, report_dir: str = "reports"):
        self.report_dir = report_dir
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

    def generate_daily_report(self, opportunities: List[Dict[str, Any]], portfolio_summary: Dict[str, Any]):
        """
        Generate a daily markdown report.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(self.report_dir, f"daily_report_{date_str}.md")
        
        with open(filename, "w") as f:
            f.write(f"# Daily Trading Report - {date_str}\n\n")
            
            # 1. Market Opportunities
            f.write("## 🚀 Market Opportunities\n")
            if opportunities:
                f.write("| Ticker | Action | Quantity | Strategy |\n")
                f.write("|--------|--------|----------|----------|\n")
                for op in opportunities:
                    f.write(f"| {op['ticker']} | **{op['action']}** | {op['quantity']} | {op.get('strategy', 'N/A')} |\n")
            else:
                f.write("> No new trading signals generated today.\n")
            
            f.write("\n")
            
            # 2. Portfolio Summary
            f.write("## 💼 Portfolio Summary\n")
            f.write(f"- **Total Value**: ${portfolio_summary.get('total_value', 0.0):,.2f}\n")
            f.write(f"- **Cash**: ${portfolio_summary.get('cash', 0.0):,.2f}\n")
            f.write(f"- **PnL**: ${portfolio_summary.get('pnl', 0.0):,.2f}\n")
            
            f.write("\n### Current Positions\n")
            positions = portfolio_summary.get('positions', {})
            if positions:
                f.write("| Ticker | Quantity |\n")
                f.write("|--------|----------|\n")
                for ticker, qty in positions.items():
                    f.write(f"| {ticker} | {qty} |\n")
            else:
                f.write("No active positions.\n")

        print(f"Report generated: {filename}")
        return filename
