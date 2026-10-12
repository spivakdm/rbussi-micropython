"""Build true-size A4 calibration and short straight-line templates."""
from pathlib import Path
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
WIDTHS_MM = (10, 6, 14)


def main():
    destination = ROOT / 'printables/day02-line-templates.pdf'
    destination.parent.mkdir(exist_ok=True)
    c = canvas.Canvas(str(destination), pagesize=A4, pageCompression=1)
    c.setTitle('RBussi Day 2 - A4 Sensor and Line Templates')
    c.setAuthor('Metropolia ICT Summer School / Dmitrii Spivak')
    page_height = A4[1]

    def text(x, top, value, size=10, bold=False, gray=0):
        c.setFillGray(gray)
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        c.drawString(x * mm, page_height - top * mm, value)

    def rectangle(x, top, width, height, fill, stroke=False):
        c.setFillGray(fill)
        c.setStrokeGray(0.65)
        c.setLineWidth(0.3)
        c.rect(x * mm, page_height - (top + height) * mm,
               width * mm, height * mm, fill=1, stroke=int(stroke))

    for page, width in enumerate(WIDTHS_MM, 1):
        text(18, 18, 'Day 2 | Sensor and Line Practice', 18, True)
        text(18, 27, f'A4 portrait | Black line: {width} mm | Straight section: 160 mm', 10)
        text(18, 35, 'Print at Actual size / 100%. Disable Fit to page. Check the 50 mm ruler.', 10, True)

        text(18, 47, 'BLACK', 10, True)
        text(70, 47, 'WHITE', 10, True)
        rectangle(18, 51, 35, 35, 0)
        rectangle(70, 51, 35, 35, 1, stroke=True)
        text(18, 92, 'Read the centres of the patches, away from edges and labels.', 9)
        for index, line in enumerate((
            '1. Measure black and white.',
            '2. Check each sensor side.',
            '3. Test the LED response.',
            '4. Start below the stripe.',
            '   Travel towards the bar.',
        )):
            text(126, 54 + 6 * index, line, 9)

        # Only the test line and stop bar occupy the lower track area.
        rectangle(105 - width / 2, 111, width, 160, 0)
        rectangle(65, 111, 80, 15, 0)

        c.setStrokeGray(0)
        c.setLineWidth(0.7)
        ruler_y = page_height - 285 * mm
        c.line(18 * mm, ruler_y, 68 * mm, ruler_y)
        for tick in range(0, 51, 10):
            x = (18 + tick) * mm
            c.line(x, ruler_y - 1.5 * mm, x, ruler_y + 1.5 * mm)
        text(18, 281, 'This ruler must measure 50 mm', 8)
        text(85, 282, 'Print one suitable width per student.', 9)
        text(85, 288, f'Metropolia ICT Summer School | RBussi | Option {page}/3', 8)
        c.showPage()

    c.save()
    output = ROOT / 'output/pdf/RBussi-Day-2-line-templates-A4.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(destination, output)
    print(output)


if __name__ == '__main__':
    main()
