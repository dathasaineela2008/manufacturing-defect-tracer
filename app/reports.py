"""CSV and PDF report helpers."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def rows_to_csv(headers: Sequence[str], rows: List[Dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row.get(h, "") for h in headers])
    return buffer.getvalue()


def rows_to_pdf(title: str, headers: Sequence[str], rows: List[Dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("MDTPS — Manufacturing Defect Traceability &amp; Prediction System", styles["Heading2"]),
        Paragraph(title, styles["Heading3"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} (academic sample data)", styles["Normal"]),
        Spacer(1, 12),
    ]
    data = [list(headers)]
    for row in rows:
        data.append([str(row.get(h, ""))[:40] for h in headers])
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2744")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9aa8b8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    return buffer.getvalue()
