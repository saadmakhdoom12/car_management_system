from fpdf import FPDF
from datetime import datetime
from typing import List, Dict, Optional
import os

class CarSystemPDF(FPDF):
    def header(self):
        # Logo
        if os.path.exists('assets/logo.png'):
            self.image('assets/logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Car Management System', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(-10, 10, datetime.now().strftime('%Y-%m-%d %H:%M'), 0, 0, 'R')

class PDFGenerator:
    def __init__(self):
        self.pdf = CarSystemPDF()
        self.pdf.alias_nb_pages()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def generate_estimate(self, estimate_data: Dict, services: List[Dict]) -> str:
        """Generate PDF for an estimate"""
        filename = f"reports/estimate_{estimate_data['estimate_id']}.pdf"
        
        # Customer Information
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Customer Information', 0, 1)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, f"Name: {estimate_data['customer_name']}", 0, 1)
        self.pdf.cell(0, 6, f"Phone: {estimate_data['customer_phone']}", 0, 1)
        self.pdf.cell(0, 6, f"Email: {estimate_data['customer_email']}", 0, 1)
        
        # Vehicle Information
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Vehicle Information', 0, 1)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, f"Make: {estimate_data['vehicle_make']}", 0, 1)
        self.pdf.cell(0, 6, f"Model: {estimate_data['vehicle_model']}", 0, 1)
        self.pdf.cell(0, 6, f"Year: {estimate_data['vehicle_year']}", 0, 1)
        self.pdf.cell(0, 6, f"VIN: {estimate_data['vehicle_vin']}", 0, 1)
        
        # Services Table
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Services', 0, 1)
        
        # Table Header
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(90, 7, 'Description', 1)
        self.pdf.cell(30, 7, 'Parts', 1)
        self.pdf.cell(30, 7, 'Labor', 1)
        self.pdf.cell(40, 7, 'Total', 1)
        self.pdf.ln()
        
        # Table Content
        self.pdf.set_font('Arial', '', 10)
        total = 0
        for service in services:
            self.pdf.cell(90, 6, service['description'], 1)
            self.pdf.cell(30, 6, f"${service['parts_cost']:.2f}", 1)
            self.pdf.cell(30, 6, f"${service['labor_cost']:.2f}", 1)
            self.pdf.cell(40, 6, f"${service['total_cost']:.2f}", 1)
            self.pdf.ln()
            total += service['total_cost']
        
        # Total
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(150, 7, 'Total:', 1)
        self.pdf.cell(40, 7, f"${total:.2f}", 1)

        # Add tax breakdown
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Price Breakdown', 0, 1)
        self.pdf.set_font('Arial', '', 10)
        
        self.pdf.cell(0, 6, f"Subtotal: ${estimate_data['subtotal']:.2f}", 0, 1)
        self.pdf.cell(0, 6, f"NHIL (2.5%): ${estimate_data['nhil']:.2f}", 0, 1)
        self.pdf.cell(0, 6, f"GETFUND (2.5%): ${estimate_data['getfund']:.2f}", 0, 1)
        self.pdf.cell(0, 6, f"COVID Levy (1%): ${estimate_data['covid_levy']:.2f}", 0, 1)
        self.pdf.cell(0, 6, f"Total with Levies: ${estimate_data['subtotal'] * 1.06:.2f}", 0, 1)
        self.pdf.cell(0, 6, f"VAT (15%): ${estimate_data['vat']:.2f}", 0, 1)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, f"Grand Total: ${estimate_data['total_amount']:.2f}", 0, 1)
        
        self.pdf.output(filename)
        return filename

    def generate_inventory_report(self, inventory_items: List[Dict]) -> str:
        """Generate PDF for inventory report"""
        filename = f"reports/inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'Inventory Report', 0, 1, 'C')
        self.pdf.ln(10)
        
        # Table Header
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 7, 'Item Code', 1)
        self.pdf.cell(80, 7, 'Description', 1)
        self.pdf.cell(30, 7, 'Quantity', 1)
        self.pdf.cell(40, 7, 'Unit Price', 1)
        self.pdf.ln()
        
        # Table Content
        self.pdf.set_font('Arial', '', 10)
        for item in inventory_items:
            self.pdf.cell(40, 6, item['item_code'], 1)
            self.pdf.cell(80, 6, item['description'], 1)
            self.pdf.cell(30, 6, str(item['quantity']), 1)
            self.pdf.cell(40, 6, f"${item['unit_price']:.2f}", 1)
            self.pdf.ln()
        
        self.pdf.output(filename)
        return filename

    def generate_service_history(self, customer_data: Dict, service_history: List[Dict]) -> str:
        """Generate PDF for service history"""
        filename = f"reports/service_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Customer Information
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Service History Report', 0, 1, 'C')
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(0, 6, f"Customer: {customer_data['name']}", 0, 1)
        self.pdf.cell(0, 6, f"Contact: {customer_data.get('phone', 'N/A')}", 0, 1)
        self.pdf.ln(10)
        
        # Service History Table
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(30, 7, 'Date', 1)
        self.pdf.cell(100, 7, 'Service', 1)
        self.pdf.cell(60, 7, 'Amount', 1)
        self.pdf.ln()
        
        self.pdf.set_font('Arial', '', 10)
        for service in service_history:
            self.pdf.cell(30, 6, service['date'], 1)
            self.pdf.cell(100, 6, service['description'], 1)
            self.pdf.cell(60, 6, f"${service['amount']:.2f}", 1)
            self.pdf.ln()
        
        self.pdf.output(filename)
        return filename

    def generate_jobcard(self, jobcard_data: Dict) -> str:
        """Generate PDF for a jobcard"""
        filename = f"reports/jobcard_{jobcard_data['jobcard_id']}.pdf"
        
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Job Card', 0, 1, 'C')
        
        # Add jobcard details
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Job Card #: {jobcard_data['jobcard_id']}", 0, 1)
        self.pdf.cell(0, 10, f"Technician: {jobcard_data['technician']}", 0, 1)
        self.pdf.cell(0, 10, f"Status: {jobcard_data['status']}", 0, 1)
        
        self.pdf.output(filename)
        return filename