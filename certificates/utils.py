import io
import cloudinary.uploader
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def generate_certificate_pdf(student_name, course_title, issued_date):
    """Generate a certificate PDF in memory and return the bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Background colour
    c.setFillColor(colors.HexColor('#1a1a2e'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Gold border
    c.setStrokeColor(colors.HexColor('#c9a84c'))
    c.setLineWidth(4)
    c.rect(1.5*cm, 1.5*cm, width - 3*cm, height - 3*cm, fill=False, stroke=True)

    # Inner border
    c.setLineWidth(1)
    c.rect(1.8*cm, 1.8*cm, width - 3.6*cm, height - 3.6*cm, fill=False, stroke=True)

    # Title
    c.setFillColor(colors.HexColor('#c9a84c'))
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(width / 2, height - 5*cm, 'CERTIFICATE')

    c.setFont('Helvetica', 18)
    c.drawCentredString(width / 2, height - 6.5*cm, 'OF COMPLETION')

    # Divider line
    c.setStrokeColor(colors.HexColor('#c9a84c'))
    c.setLineWidth(1)
    c.line(4*cm, height - 7.5*cm, width - 4*cm, height - 7.5*cm)

    # Body text
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 9*cm, 'This is to certify that')

    # Student name
    c.setFillColor(colors.HexColor('#c9a84c'))
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(width / 2, height - 11*cm, student_name)

    # Divider under name
    c.setStrokeColor(colors.HexColor('#c9a84c'))
    c.setLineWidth(0.5)
    c.line(5*cm, height - 11.8*cm, width - 5*cm, height - 11.8*cm)

    # Course text
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 13*cm, 'has successfully completed the course')

    # Course title
    c.setFillColor(colors.HexColor('#c9a84c'))
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(width / 2, height - 14.5*cm, course_title)

    # Date
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 12)
    c.drawCentredString(width / 2, height - 17*cm, f'Issued on {issued_date}')

    # Institute name
    c.setFillColor(colors.HexColor('#c9a84c'))
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(width / 2, height - 18.5*cm, 'Arabic Institute')

    c.save()
    buffer.seek(0)
    return buffer


def upload_certificate_to_cloudinary(student_name, course_title, issued_date):
    """Generate and upload certificate PDF to Cloudinary, return the URL."""
    pdf_buffer = generate_certificate_pdf(student_name, course_title, issued_date)

    # Create a safe filename
    safe_name = student_name.replace(' ', '_').replace('@', '_at_')
    safe_course = course_title.replace(' ', '_')
    public_id = f'certificates/{safe_name}_{safe_course}_{issued_date}'

    result = cloudinary.uploader.upload(
        pdf_buffer,
        public_id=public_id,
        resource_type='raw',
        format='pdf',
        overwrite=True,
    )

    return result['secure_url']