# from io import BytesIO
# from django.template.loader import render_to_string
# from xhtml2pdf import pisa

# def generate_receipt_pdf(receipt):
#     html = render_to_string("receipt_pdf.html", {"receipt": receipt})
#     result = BytesIO()

#     pdf = pisa.CreatePDF(
#         html,
#         dest=result,
#         encoding="UTF-8"
#     )

#     if pdf.err:
#         return None

#     return result.getvalue()

# utility.py
# from io import BytesIO
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from reportlab.lib.units import mm


# def generate_receipt_pdf(receipt, assets):
#     """
#     assets = {
#         "LOGO_URL": "...",
#         "TEMPLE_BG_URL": "...",
#         "DEITY_URL": "...",
#         "SIGNATURE_URL": "..."
#     }
#     """

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4

#     # ---------- Background ----------
#     if assets.get("TEMPLE_BG_URL"):
#         bg = ImageReader(assets["TEMPLE_BG_URL"])
#         c.drawImage(
#             bg,
#             0,
#             0,
#             width=width,
#             height=height,
#             mask="auto"
#         )

#     # ---------- Logo ----------
#     if assets.get("LOGO_URL"):
#         logo = ImageReader(assets["LOGO_URL"])
#         c.drawImage(
#             logo,
#             20 * mm,
#             height - 40 * mm,
#             width=30 * mm,
#             height=30 * mm,
#             mask="auto"
#         )

#     # ---------- Title ----------
#     c.setFont("Helvetica-Bold", 18)
#     c.drawCentredString(
#         width / 2,
#         height - 30 * mm,
#         "Donation Receipt"
#     )

#     # ---------- Receipt Details ----------
#     c.setFont("Helvetica", 11)

#     y = height - 60 * mm
#     line_gap = 8 * mm

#     c.drawString(30 * mm, y, f"Receipt No: {receipt.receipt_id}")
#     y -= line_gap

#     c.drawString(30 * mm, y, f"Donor Name: {receipt.donor_name}")
#     y -= line_gap

#     c.drawString(30 * mm, y, f"Amount: ₹ {receipt.donation_amount}")
#     y -= line_gap

#     if receipt.pan_number:
#         c.drawString(30 * mm, y, f"PAN: {receipt.pan_number}")
#         y -= line_gap
        
#     c.drawString(30 * mm, y, f"Date: {receipt.created_at.strftime('%d-%m-%Y')}")
#     y -= line_gap

#     c.drawString(30 * mm, y, f"Purpose: General Donation")
    
#     c.drawString(
#         30 * mm,
#         y,
#         f"Address: {receipt.address}, {receipt.district}, {receipt.state} - {receipt.pincode}",
#     )

#     # ---------- Deity Image ----------
#     if assets.get("DEITY_URL"):
#         deity = ImageReader(assets["DEITY_URL"])
#         c.drawImage(
#             deity,
#             width - 70 * mm,
#             height - 120 * mm,
#             width=40 * mm,
#             height=50 * mm,
#             mask="auto"
#         )

#     # ---------- Signature ----------
#     if assets.get("SIGNATURE_URL"):
#         sign = ImageReader(assets["SIGNATURE_URL"])
#         c.drawImage(
#             sign,
#             width - 70 * mm,
#             30 * mm,
#             width=40 * mm,
#             height=20 * mm,
#             mask="auto"
#         )

#         c.setFont("Helvetica", 9)
#         c.drawString(width - 70 * mm, 25 * mm, "Authorized Signature")

#     # ---------- Footer ----------
#     c.setFont("Helvetica-Oblique", 9)
#     c.drawCentredString(
#         width / 2,
#         15 * mm,
#         "This is a system-generated receipt"
#     )

#     c.showPage()
#     c.save()

#     pdf = buffer.getvalue()
#     buffer.close()
#     return pdf


# utils.py
from io import BytesIO
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_receipt_pdf(receipt, assets):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)


    LEFT = 20 * mm
    RIGHT = width - 20 * mm

    # -------------------------------------------------
    # Decorative Border
    # -------------------------------------------------
    c.setStrokeColorRGB(0.83, 0.63, 0.09)  # gold
    c.setLineWidth(6)
    c.rect(10, 10, width - 20, height - 20)

    # -------------------------------------------------
    # Watermarks
    # -------------------------------------------------
    c.saveState()
    if assets.get("TEMPLE_BG_URL"):
        c.setFillAlpha(0.04)
        temple_bg = ImageReader(assets["TEMPLE_BG_URL"])
        c.drawImage(
            temple_bg,
            width * 0.15,
            height * 0.25,
            width=width * 0.7,
            height=height * 0.5,
            preserveAspectRatio=True,
            mask="auto",
        )

    if assets.get("DEITY_URL"):
        c.setFillAlpha(0.06)
        deity = ImageReader(assets["DEITY_URL"])
        c.drawImage(
            deity,
            LEFT,
            60,
            width=60 * mm,
            height=90 * mm,
            preserveAspectRatio=True,
            mask="auto",
        )
    c.restoreState()
    # -------------------------------------------------
    # Header
    # -------------------------------------------------
    if assets.get("LOGO_URL"):
        logo = ImageReader(assets["LOGO_URL"])
        c.drawImage(
            logo,
            RIGHT - 90,
            height - 120,
            width=90,
            height=90,
            mask="auto",
        )

    c.setFont("Times-Bold", 20)
    c.setFillColor(colors.darkred)
    c.drawCentredString(
        width / 2,
        height - 60,
        "SHRI VAISHNO MATA JI MANDIR GAYATRI DHAM",
    )

    c.setFont("Times-Roman", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(
        width / 2,
        height - 82,
        "Registered Office: Sajawn, Deoria, Uttar Pradesh – 274508",
    )
    c.drawCentredString(width / 2, height - 98, "PAN: ABHTS1443H")

    c.setFont("Times-Bold", 16)
    c.drawCentredString(width / 2, height - 130, "Donation Receipt")

    # -------------------------------------------------
    # Meta Row
    # -------------------------------------------------
    c.setFont("Times-Roman", 12)
    c.drawString(
        LEFT,
        height - 160,
        f"Receipt No: {receipt.receipt_id}",
    )
    c.drawRightString(
        RIGHT,
        height - 160,
        f"Printed On: {receipt.created_at.strftime('%d/%m/%Y')}",
    )

    # -------------------------------------------------
    # Table Data
    # -------------------------------------------------
    table_data = [
        ["Received With Thanks From", receipt.donor_name],
        [
            "Address",
            f"{receipt.address}, {receipt.district}, "
            f"{receipt.state} – {receipt.pincode}\n{receipt.country}",
        ],
        ["PAN Number", receipt.pan_number or "—"],
        ["Mobile Number", receipt.mobile],
        ["Email ID", receipt.email],
        ["Purpose of Donation", "General Donation"],
        ["Mode of Donation", "Online"],
        ["Date of Donation", receipt.created_at.strftime("%d/%m/%Y")],
        ["Amount of Donation", f"₹ {receipt.donation_amount}"],
    ]

    table = Table(
        table_data,
        colWidths=[70 * mm, width - 100 * mm],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Times-Roman", 12),
                ("FONT", (0, 0), (0, -1), "Times-Bold", 12),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    table.wrapOn(c, width, height)
    table.drawOn(c, LEFT, height - 520)

    # -------------------------------------------------
    # Signature
    # -------------------------------------------------
    if assets.get("SIGNATURE_URL"):
        sign = ImageReader(assets["SIGNATURE_URL"])
        c.drawImage(
            sign,
            RIGHT - 160,
            120,
            width=140,
            height=50,
            mask="auto",
        )

    c.setFont("Times-Bold", 12)
    c.drawRightString(RIGHT, 105, "Authorized Signatory")
    c.setFont("Times-Roman", 11)
    c.drawRightString(RIGHT, 90, "(Treasurer)")

    # -------------------------------------------------
    # Footer
    # -------------------------------------------------
    c.setFont("Times-Roman", 11)
    c.drawString(
        LEFT,
        70,
        "• 50% of voluntary contribution is eligible for deduction under "
        "Section 80G(2)(b) of the Income Tax Act, 1961.",
    )
    c.drawString(
        LEFT,
        52,
        "• This is a system-generated receipt and does not require a physical signature.",
    )
    c.drawString(
        LEFT,
        34,
        "Contact: support@exampletrust.org | Website: www.exampletrust.org",
    )

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

