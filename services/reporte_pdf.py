# services/reporte_pdf.py
# Servicio para generar reportes en PDF

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os
import tempfile

class ReportePDF:
    """Clase para generar reportes en PDF"""
    
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []
    
    def add_title(self, title):
        """Agrega título al reporte"""
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        self.elements.append(Paragraph(title, title_style))
        self.elements.append(Spacer(1, 0.2 * inch))
    
    def add_date(self):
        """Agrega fecha actual"""
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontSize=10
        )
        fecha = f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        self.elements.append(Paragraph(fecha, date_style))
        self.elements.append(Spacer(1, 0.2 * inch))
    
    def add_table(self, data, headers):
        """Agrega una tabla al reporte"""
        table_data = [headers] + data
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        self.elements.append(table)
    
    def generate(self):
        """Genera el PDF"""
        self.doc.build(self.elements)
        return True

def generar_reporte_productos(productos):
    """Genera reporte PDF de productos"""
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f'reporte_productos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    
    reporte = ReportePDF(filename)
    reporte.add_title("Reporte de Productos")
    reporte.add_title("Patronato de Catacocha")
    reporte.add_date()
    
    headers = ['ID', 'Nombre', 'Descripción', 'Precio', 'Stock']
    data = []
    for p in productos:
        data.append([
            str(p.id_producto),
            p.nombre,
            p.descripcion or '',
            f'${p.precio:.2f}',
            str(p.stock)
        ])
    
    reporte.add_table(data, headers)
    reporte.generate()
    
    return filename
