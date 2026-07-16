import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

def obter_cabecalho_loja(styles):
    title_style = ParagraphStyle('CabecalhoTitulo', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=3)
    sub_style = ParagraphStyle('CabecalhoSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#4A5568'), alignment=1, spaceAfter=2)
    return [
        Paragraph("<b>MASTER TECH TELECOMUNICAÇÕES E INFORMÁTICA</b>", title_style),
        Paragraph("Avenida Principal, Centro - Goiânia - GO", sub_style),
        Paragraph("Telefone / WhatsApp: (62) 98570-3663", sub_style),
        Spacer(1, 10)
    ]

def gerar_pdf_recibo(venda_id, produto, qtd, total, pagamento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#2D3748'), spaceAfter=8)
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

    story.extend(obter_cabecalho_loja(styles))
    story.append(Paragraph(f"<b>RECIBO DE VENDA Nº {venda_id}</b>", ParagraphStyle('ReciboNum', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=10)))
    
    dados = [
        [Paragraph("<b>Item / Produto</b>", bold_style), Paragraph(str(produto), normal_style)],
        [Paragraph("<b>Quantidade</b>", bold_style), Paragraph(str(qtd), normal_style)],
        [Paragraph("<b>Forma de Pagamento</b>", bold_style), Paragraph(str(pagamento), normal_style)],
        [Paragraph("<b>Valor Total</b>", bold_style), Paragraph(f"R$ {total:.2f}", bold_style)]
    ]
    t = Table(dados, colWidths=[150, 350])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')), ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F7FAFC')), ('PADDING', (0,0), (-1,-1), 8), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_os(os_id, cliente, telefone, tipo, modelo, serie, estado, defeito, valor, status, data_entrada, data_aprovacao="", data_pronto="", data_retirada=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('OSNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2D3748'), spaceAfter=6)
    bold_style = ParagraphStyle('OSBold', parent=normal_style, fontName='Helvetica-Bold')

    def criar_via(via_nome):
        elements = []
        elements.extend(obter_cabecalho_loja(styles))
        elements.append(Paragraph(f"<b>O.S. Nº {os_id} - {via_nome}</b>", ParagraphStyle('Via', parent=styles['Heading2'], alignment=1)))
        elements.append(Paragraph(f"<b>Situação:</b> {status} | <b>Entrada:</b> {data_entrada}", normal_style))
        elements.append(Paragraph(f"<b>Cliente:</b> {cliente} | <b>Aparelho:</b> {tipo} {modelo}", normal_style))
        elements.append(Paragraph(f"<b>Valor Estimado:</b> R$ {valor:.2f}", bold_style))
        elements.append(Spacer(1, 10))
        return elements

    story.extend(criar_via("Via do Cliente"))
    story.append(Spacer(1, 20))
    story.extend(criar_via("Via da Loja"))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_recibo_entrega(os_id, cliente, telefone, tipo, modelo, serie, defeito_constatado, pecas_usadas, valor, data_entrega, garantia, forma_pagamento=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    story.extend(obter_cabecalho_loja(styles))
    
    dados = [
        ["Cliente:", cliente, "Valor Pago:", f"R$ {valor:.2f}"],
        ["Serviço:", defeito_constatado, "Forma Pagto:", forma_pagamento]
    ]
    t = Table(dados, colWidths=[80, 200, 80, 100])
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()