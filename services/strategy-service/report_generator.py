# algo-bot/services/strategy-service/report_generator.py

from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Quantitative Backtest Report: L99 Dual-Engine', border=0, ln=1, align='C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(trade_data, filename="L99_Backtest_Report.pdf"):
    print("\n📝 Compiling PDF Report...")
    pdf = PDFReport()
    pdf.add_page()
    
    # Table Header Configuration
    columns = ['Date', 'Time', 'Analysis / Setup', 'Dir', 'Entry', 'Exit', 'PnL (Pts)']
    col_widths = [25, 20, 35, 15, 25, 25, 30]
    
    # Draw Headers
    pdf.set_font("Arial", 'B', 9)
    for i, col in enumerate(columns):
        pdf.cell(col_widths[i], 10, col, border=1, align='C')
    pdf.ln()
    
    # Draw Rows
    pdf.set_font("Arial", size=9)
    total_pnl = 0.0
    
    for trade in trade_data:
        pdf.cell(col_widths[0], 10, str(trade['date']), border=1, align='C')
        pdf.cell(col_widths[1], 10, str(trade['time']), border=1, align='C')
        pdf.cell(col_widths[2], 10, str(trade['setup']), border=1, align='C')
        pdf.cell(col_widths[3], 10, str(trade['direction'])[:3], border=1, align='C') # Shorten UPSIDE to UPS
        pdf.cell(col_widths[4], 10, f"{trade['entry']:.2f}", border=1, align='C')
        pdf.cell(col_widths[5], 10, f"{trade['exit']:.2f}", border=1, align='C')
        
        # Color code the PnL
        pnl = trade['pnl']
        total_pnl += pnl
        if pnl > 0:
            pdf.set_text_color(0, 128, 0) # Green
        else:
            pdf.set_text_color(220, 0, 0) # Red
            
        pdf.cell(col_widths[6], 10, f"{pnl:.2f}", border=1, align='C')
        pdf.set_text_color(0, 0, 0) # Reset to black
        pdf.ln()
        
    # Draw Summary Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 128, 0) if total_pnl > 0 else pdf.set_text_color(220, 0, 0)
    pdf.cell(0, 10, f"Net Spot Points Captured: {total_pnl:.2f}", border=0, ln=1, align='R')
    
    pdf.output(filename)
    print(f"✅ PDF Report saved to: {filename}")