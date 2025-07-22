#!/usr/bin/env python3
"""
Bank Statement to Journal Entry Processor
Converts PDF bank statements to Excel-ready journal entries using regex matching
"""

import re
import pandas as pd
import PyPDF2
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import sys
import os
import subprocess
import platform

class BankStatementProcessor:
    def __init__(self):
        # Refined vendor patterns based on actual Chase statement data
        self.vendors = {
            100: {"name": "Tampa International Airport", "patterns": [r"tampa.*int.*airpor"], "default_acct": 374},
            101: {"name": "Epcor Water (1)", "patterns": [r"epcor.*water.*usa", r"epcor.*water.*\(usa\)"], "default_acct": 352},
            102: {"name": "Epcor Water (2)", "patterns": [r"epcor.*water.*usa", r"epcor.*water.*\(usa\)"], "default_acct": 352},
            103: {"name": "ADT Security", "patterns": [r"adt.*security.*ser", r"adt.*security", r"adt"], "default_acct": 383},
            104: {"name": "American Airlines", "patterns": [r"american.*air", r"southwest", r"southwes"], "default_acct": 370},
            105: {"name": "HCAA Prebookpark", "patterns": [r"hcaa.*prebook", r"prebookpark"], "default_acct": 374},
            106: {"name": "Cox Communications", "patterns": [r"cox.*comm", r"cox.*phx"], "default_acct": 360},
            107: {"name": "Queen of All Saints Chapel Inc.", "patterns": [r"queen.*saints", r"seminary"], "default_acct": 210},
            108: {"name": "CHK ...0784", "patterns": [r"chk.*0784", r"fraser.*chase", r"check.*#", r"^\d+\s+\^"], "default_acct": 175},
            109: {"name": "Southwest Gas", "patterns": [r"southwest.*gas"], "default_acct": 351},
            200: {"name": "Misc. Vendors", "patterns": [], "default_acct": 410},  # Catch-all
            500: {"name": "Fr. Luke Petrizzi", "patterns": [r"fr\.?\s*luke.*petrizzi", r"luke.*petrizzi"], "default_acct": 376},
            501: {"name": "Ron Pardini", "patterns": [r"ron.*pardini"], "default_acct": 385},
            502: {"name": "Fr. Nicolas Despósito", "patterns": [r"fr\.?\s*nicolas.*desp", r"nicolas.*desp"], "default_acct": 376}
        }
        
        # Enhanced transaction patterns for better account classification
        self.transaction_patterns = {
            # Travel & Lodging (370-376)
            370: [r"airline", r"airfare", r"flight", r"american.*air", r"southwest", r"southwes"],
            371: [r"rental.*car", r"hertz", r"enterprise", r"budget.*rent"],
            372: [r"hotel", r"inn", r"resort", r"accommodation", r"lodging", r"holiday.*inn"],
            373: [r"taco.*bell", r"starbucks", r"peet", r"mcdonalds", r"wendy", r"culver", 
                  r"dunkin", r"dairy.*queen", r"tropical.*smoothie"],
            374: [r"parking", r"toll", r"taxi", r"uber", r"lyft", r"tampa.*int.*airpor"],
            375: [r"fuel", r"gas.*station", r"marathon", r"circle.*k", r"wawa", r"gas.*\d+"],
            376: [r"reimbursement", r"fr\.?\s*luke", r"fr\.?\s*nicolas"],
            
            # Utilities (350-352)
            350: [r"electric", r"power", r"energy"],
            351: [r"natural.*gas", r"southwest.*gas"],
            352: [r"water", r"sewer", r"epcor.*water"],
            
            # Internet & Phone (360-361)
            360: [r"internet", r"cable", r"communications", r"century.*link", r"cox.*comm"],
            361: [r"cell", r"mobile", r"phone"],
            
            # Office & Supplies (380-386)
            380: [r"office", r"supplies", r"depot", r"office.*depot"],
            381: [r"postage", r"ups", r"fedex", r"usps"],
            382: [r"printing", r"copy", r"deluxe.*small.*bus"],
            383: [r"subscription", r"dues", r"security.*system", r"adt.*security", r"news.*shop", 
                  r"phoenix.*news", r"phx.*\d+.*news", r"bay.*to.*bay.*news", r"^bay.*to.*bay.*news"],
            384: [r"software", r"technology"],
            385: [r"church.*supplies", r"sacristy", r"autom", r"vestments"],
            386: [r"vestments", r"apparel"],
            
            # Building & Maintenance (330-338)
            330: [r"landscaping", r"lawn", r"garden"],
            331: [r"equipment", r"appliance", r"home.*depot", r"the.*home.*depot"],
            332: [r"heating", r"cooling", r"hvac"],
            333: [r"electric.*repair"],
            334: [r"plumbing"],
            335: [r"structural", r"repair"],
            336: [r"alarm"],
            337: [r"waste", r"garbage", r"trash"],
            338: [r"pest.*control"],
            
            # Special accounts
            175: [r"mortgage", r"mtg", r"chk.*\d+", r"^\d+\s+\^"],
            201: [r"deposit", r"collection"],
            210: [r"seminary.*tax", r"tax"],
            301: [r"payroll", r"salary", r"wages"],
            410: [r"miscellaneous", r"unknown", r"ebay", r"trip.*advisor"]
        }

    def copy_to_clipboard(self, text: str):
        """Copy text to system clipboard"""
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["pbcopy"], input=text, text=True, check=True)
            elif system == "Linux":
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            elif system == "Windows":
                subprocess.run(["clip"], input=text, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def extract_statement_date(self, text: str) -> Optional[str]:
        """Extract statement date from PDF text to determine filename"""
        # Look for common statement date patterns
        patterns = [
            r'(\w{3}\s+\d{1,2},\s+\d{4})\s+through\s+(\w{3}\s+\d{1,2},\s+\d{4})',
            r'Statement\s+Period:\s*(\w{3}\s+\d{1,2},\s+\d{4})\s*-\s*(\w{3}\s+\d{1,2},\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})\s+through\s+(\d{1,2}/\d{1,2}/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                end_date_str = match.group(2)
                try:
                    # Parse the end date to get month/year
                    if '/' in end_date_str:
                        end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
                    else:
                        end_date = datetime.strptime(end_date_str, '%b %d, %Y')
                    return end_date.strftime('%m-%Y')
                except ValueError:
                    continue
        
        # Fallback to current month/year
        return datetime.now().strftime('%m-%Y')

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def parse_transaction_line(self, line: str) -> Optional[Dict]:
        """Parse a single transaction line using regex patterns"""
        line = line.strip()
        
        # Chase-specific patterns (refined)
        chase_patterns = [
            # Card Purchase pattern: MM/DD Card Purchase MM/DD Description Amount
            r'(\d{2}/\d{2})\s+Card\s+Purchase\s+(\d{2}/\d{2})\s+(.+?)\s+\$?(\d+\.?\d*)$',
            # Card Purchase with Pin pattern
            r'(\d{2}/\d{2})\s+Card\s+Purchase\s+With\s+Pin\s+(\d{2}/\d{2})\s+(.+?)\s+\$?(\d+\.?\d*)$',
            # Deposit pattern with dollar sign: MM/DD Deposit Number $Amount
            r'(\d{2}/\d{2})\s+Deposit\s+(\d+)\s+\$(\d{1,3}(?:,\d{3})*\.?\d*)$',
            # Deposit pattern without dollar sign: MM/DD Deposit Number Amount
            r'(\d{2}/\d{2})\s+Deposit\s+(\d+)\s+(\d{1,3}(?:,\d{3})*\.?\d*)$',
            # Check pattern: Number ^ MM/DD $Amount
            r'(\d+)\s+\^\s+(\d{2}/\d{2})\s+\$(\d+\.?\d*)$',
            # Electronic withdrawal pattern: MM/DD Orig CO Name:... Amount
            r'(\d{2}/\d{2})\s+Orig\s+CO\s+Name:(.+?)\s+Orig\s+ID:.+?\s+\$(\d+\.?\d*)$'
        ]
        
        # Try Chase-specific patterns first
        for pattern in chase_patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    if 'Card Purchase' in line:
                        return {
                            'date': groups[1],  # Transaction date
                            'amount': f"-{groups[3]}",  # Negative for purchases
                            'description': groups[2].strip()
                        }
                    elif 'Deposit' in line:
                        amount = groups[2].replace(',', '') if len(groups) > 2 else groups[2]
                        return {
                            'date': groups[0],
                            'amount': amount,  # Positive for deposits
                            'description': f"Deposit {groups[1]}"
                        }
                    elif '^' in line:  # Check
                        return {
                            'date': groups[1],
                            'amount': f"-{groups[2]}",  # Negative for checks
                            'description': f"Check #{groups[0]}"
                        }
                    elif 'Orig CO Name' in line:
                        company = groups[1].split(' Orig ID')[0]
                        return {
                            'date': groups[0],
                            'amount': f"-{groups[2]}",  # Negative for withdrawals
                            'description': company
                        }
        
        # Generic patterns as fallback
        generic_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]?\d{2,4})\s+([+-]?\$?[\d,]+\.?\d*)\s+(.+)',
            r'([+-]?\$?[\d,]+\.?\d*)\s+(\d{1,2}[-/]\d{1,2}[-/]?\d{2,4})\s+(.+)',
            r'(.+?)\s+([+-]?\$?[\d,]+\.?\d*)\s+(\d{1,2}[-/]\d{1,2}[-/]?\d{2,4})'
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                date_str, amount_str, description = None, None, None
                
                for group in groups:
                    if re.match(r'\d{1,2}[-/]\d{1,2}[-/]?\d{2,4}', group):
                        date_str = group
                    elif re.match(r'[+-]?\$?[\d,]+\.?\d*', group):
                        amount_str = group
                    else:
                        description = group
                
                if date_str and amount_str and description:
                    return {
                        'date': date_str,
                        'amount': amount_str,
                        'description': description.strip()
                    }
        return None

    def identify_vendor(self, description: str) -> Tuple[int, str]:
        """Identify vendor using regex patterns"""
        desc_lower = description.lower()
        
        # Check specific vendor patterns first
        for vnbr, vendor_info in self.vendors.items():
            if vnbr == 200:  # Skip misc vendors for now
                continue
            for pattern in vendor_info["patterns"]:
                if re.search(pattern, desc_lower):
                    return vnbr, vendor_info["name"]
        
        # If no specific vendor found, return misc vendors
        return 200, "Misc. Vendors"

    def classify_account(self, description: str, vendor_nbr: int) -> int:
        """Classify transaction to appropriate account number"""
        desc_lower = description.lower()
        
        # Check transaction patterns first for more specific classification
        for acct_nbr, patterns in self.transaction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, desc_lower):
                    return acct_nbr
        
        # Then check if vendor has a default account
        if vendor_nbr in self.vendors:
            default_acct = self.vendors[vendor_nbr]["default_acct"]
            if default_acct:
                return default_acct
        
        # Default to miscellaneous
        return 410

    def process_bank_statement(self, pdf_path: str) -> Tuple[List[Dict], str]:
        """Process entire bank statement and return journal entries and statement date"""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return [], ""
        
        # Extract statement date for filename
        statement_date = self.extract_statement_date(text)
        
        lines = text.split('\n')
        transactions = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Skip header lines and non-transaction lines
            if any(keyword in line.lower() for keyword in 
                   ['date', 'description', 'amount', 'balance', 'statement', 'account', 'customer service']):
                continue
            
            transaction = self.parse_transaction_line(line)
            if transaction:
                vnbr, vendor_name = self.identify_vendor(transaction['description'])
                acct_nbr = self.classify_account(transaction['description'], vnbr)
                
                # Clean amount
                amount_str = re.sub(r'[^\d.-]', '', transaction['amount'])
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0
                
                # Determine transaction type
                trans_type = "Debit" if amount < 0 else "Credit"
                
                # Flag unclassified transactions
                classification_note = ""
                if vnbr == 200 and acct_nbr == 410:
                    classification_note = "⚠️ NEEDS MANUAL REVIEW ⚠️"
                
                journal_entry = {
                    'Date': transaction['date'],
                    'Type': trans_type,
                    'Check #': '',
                    'Vendor/Bank': vendor_name,
                    'Description': transaction['description'],
                    'Cleared': transaction['date'],
                    'Debit (-)': abs(amount) if amount < 0 else '',
                    'Credit (+)': amount if amount > 0 else '',
                    'Balance': '',  # Would need running calculation
                    'VNbr': vnbr,
                    'AcctNbr': acct_nbr,
                    'Classification_Note': classification_note,
                    'Source_Line': line_num
                }
                
                transactions.append(journal_entry)
        
        return transactions, statement_date

    def export_to_excel(self, transactions: List[Dict], output_file: str, copy_clipboard: bool = True):
        """Export transactions to Excel format and optionally copy to clipboard"""
        if not transactions:
            print("No transactions to export")
            return
        
        df = pd.DataFrame(transactions)
        
        # Reorder columns to match your format
        column_order = ['Date', 'Type', 'Check #', 'Vendor/Bank', 'Description', 
                       'Cleared', 'Debit (-)', 'Credit (+)', 'Balance', 'VNbr', 'AcctNbr']
        
        # Add any missing columns
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[column_order + ['Classification_Note', 'Source_Line']]
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"✅ Exported {len(transactions)} transactions to {output_file}")
        
        # Copy date range to clipboard if requested
        if copy_clipboard and transactions:
            dates = [t['Date'] for t in transactions if t['Date']]
            if dates:
                date_range = f"Statement period: {min(dates)} to {max(dates)}"
                if self.copy_to_clipboard(date_range):
                    print(f"📋 Copied to clipboard: {date_range}")
                else:
                    print("⚠️  Could not copy to clipboard (install xclip on Linux)")
        
        # Print summary of unclassified items
        unclassified = df[df['Classification_Note'].str.contains('MANUAL REVIEW', na=False)]
        if not unclassified.empty:
            print(f"\n⚠️  {len(unclassified)} transactions need manual review:")
            for _, row in unclassified.iterrows():
                print(f"   Line {row['Source_Line']}: {row['Description']}")
        else:
            print(f"\n🎉 All transactions classified successfully!")

def main():
    parser = argparse.ArgumentParser(description='Process bank statement PDF to journal entries')
    parser.add_argument('pdf_file', help='Path to bank statement PDF')
    parser.add_argument('-o', '--output', default=None, 
                       help='Output Excel file (default: auto-generated MM-YYYY.xlsx)')
    parser.add_argument('--no-clipboard', action='store_true',
                       help='Skip copying date range to clipboard')
    
    args = parser.parse_args()
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_file):
        print(f"❌ Error: PDF file '{args.pdf_file}' not found")
        sys.exit(1)
    
    print(f"🔄 Processing {args.pdf_file}...")
    
    processor = BankStatementProcessor()
    transactions, statement_date = processor.process_bank_statement(args.pdf_file)
    
    if not transactions:
        print("❌ No transactions found in the PDF")
        sys.exit(1)
    
    # Generate output filename if not provided
    if args.output is None:
        output_file = f"{statement_date}.xlsx"
    else:
        output_file = args.output
    
    print(f"📊 Found {len(transactions)} transactions")
    processor.export_to_excel(transactions, output_file, not args.no_clipboard)
    
    # Show completion message
    abs_path = os.path.abspath(output_file)
    print(f"✨ Complete! File saved as: {abs_path}")

if __name__ == "__main__":
    main()
