import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

def obter_cabecalho_loja(styles):
    title_style = ParagraphStyle('CabecalhoTitulo', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=3)
    sub_style = ParagraphStyle('CabecalhoSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#4A5568'), alignment=1, spaceAfter=2)
    phone_style = ParagraphStyle('TelefoneDestaque', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=2)
    
    return [
        Paragraph("<b>MASTER TECH TELECOMUNICAÇÕES E INFORMÁTICA</b>", title_style),
        Paragraph("Avenida Aderup, N° 387, Bairro- Vila Canãa, Goiânia - GO, 74.415-010", sub_style),
        Paragraph("CNPJ: 11.030.539/0001-00", sub_style),
        Paragraph("Telefone/WhatsApp: (62) 98647-3217", phone_style),
        Spacer(1, 10)
    ]

def campos_extras_loja(styles):
    body_style = ParagraphStyle('Campos', parent=styles['Normal'], fontName='Helvetica', fontSize=10, spaceBefore=5, spaceAfter=5)
    return [
        Spacer(1, 10),
        Paragraph("<b>Serviço a ser executado:</b>", body_style),
        Paragraph("__________________________________________________________________", body_style),
        Paragraph("__________________________________________________________________", body_style),
        Spacer(1, 5),
        Paragraph("<b>Valor para o reparo: R$ __________________</b>", body_style),
        Spacer(1, 5),
        Paragraph("<b>Datas:</b> Orçamento: ___/___/___ | Aut.: ___/___/___ | Pronto: ___/___/___ | Ent.: ___/___/___", body_style),
        Spacer(1, 15),
        Paragraph("____________________________________________________", body_style),
        Paragraph("Assinatura do Cliente", body_style)
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
    
    def criar_via(via_nome):
        elements = []
        elements.extend(obter_cabecalho_loja(styles))
        elements.append(Paragraph(f"<b>O.S. Nº {os_id} - {via_nome}</b>", ParagraphStyle('Via', parent=styles['Heading2'], alignment=1)))
        elements.append(Paragraph(f"<b>Situação:</b> {status} | <b>Entrada:</b> {data_entrada}", ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)))
        elements.append(Paragraph(f"<b>Cliente:</b> {cliente} | <b>Tel:</b> {telefone}", ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)))
        elements.append(Paragraph(f"<b>Aparelho:</b> {tipo} {modelo} | <b>Série:</b> {serie}", ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)))
        elements.append(Paragraph(f"<b>Estado:</b> {estado}", ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)))
        elements.append(Paragraph(f"<b>Defeito Reclamado:</b> {defeito}", ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10)))
        elements.append(Paragraph(f"<b>Valor Estimado:</b> R$ {valor:.2f}", ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)))
        if via_nome == "Via da Loja":
            elements.extend(campos_extras_loja(styles))
        return elements

    story.extend(criar_via("Via do Cliente"))
    story.append(Spacer(1, 50)) 
    story.append(Paragraph("---------------------------------------------------------------------------------------------------------------------------", styles['Normal']))
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
    story.append(Paragraph(f"<b>RECIBO DE ENTREGA - O.S. {os_id}</b>", ParagraphStyle('Title', alignment=1, fontSize=14, spaceAfter=20)))
    dados = [
        ["Cliente:", cliente, "Telefone:", telefone],
        ["Aparelho:", f"{tipo} {modelo}", "Série:", serie],
        ["Serviço Executado:", defeito_constatado, "Garantia:", garantia],
        ["Peças Usadas:", pecas_usadas, "Forma Pagto:", forma_pagamento]
    ]
    t = Table(dados, colWidths=[100, 200, 80, 100])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))
    story.append(t)
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Valor Total:</b> R$ {valor:.2f}", styles['Normal']))
    story.append(Paragraph(f"<i>Valor por extenso: __________________________________________________________________</i>", styles['Normal']))
    story.append(Spacer(1, 40))
    assinaturas = [["____________________________", "____________________________"], ["Assinatura do Cliente", "Assinatura Atendente (Master Tech)"]]
    t_ass = Table(assinaturas, colWidths=[250, 250])
    story.append(t_ass)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()