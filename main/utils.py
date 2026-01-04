from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def generate_receipt_pdf(receipt):
    html = render_to_string("receipt_pdf.html", {"receipt": receipt})
    result = BytesIO()

    pdf = pisa.CreatePDF(
        html,
        dest=result,
        encoding="UTF-8"
    )

    if pdf.err:
        return None

    return result.getvalue()
