import csv
from datetime import datetime
from io import BytesIO, StringIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.database import orders_collection

router = APIRouter(prefix="/reports", tags=["Reports"])


# Helper: Run Aggregation
async def run_summary_pipeline(start_date: datetime, end_date: datetime):
    pipeline = [
        {"$match": {"order_date": {"$gte": start_date, "$lte": end_date}}},
        {
            "$group": {
                "_id": {"vendor_id": "$vendor_id", "status": "$status"},
                "total_orders": {"$sum": 1},
                "total_amount": {"$sum": "$total_amount"},
            }
        },
    ]

    cursor = orders_collection.aggregate(pipeline)
    results = []

    async for row in cursor:
        results.append(
            {
                "vendor_id": str(row["_id"]["vendor_id"]),
                "status": row["_id"]["status"],
                "total_orders": row["total_orders"],
                "total_amount": row["total_amount"],
            }
        )

    return results


# JSON Summary
@router.get("/summary")
async def get_order_summary(start: str, end: str):
    try:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
    except:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    data = await run_summary_pipeline(start_date, end_date)
    return data


# PDF Export
@router.get("/summary/pdf")
async def export_summary_pdf(start: str, end: str):
    try:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
    except:
        raise HTTPException(status_code=400, detail="Invalid date format")

    data = await run_summary_pipeline(start_date, end_date)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica", 16)
    p.drawString(50, 750, "Order Summary Report")

    p.setFont("Helvetica", 12)
    p.drawString(50, 730, f"Date Range: {start} to {end}")

    y = 700
    for row in data:
        text = f"Vendor: {row['vendor_id']} | Status: {row['status']} | Orders: {row['total_orders']} | Amount: ${row['total_amount']:.2f}"
        p.drawString(50, y, text)
        y -= 20
        if y < 40:
            p.showPage()
            y = 750

    p.showPage()
    p.save()

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=summary.pdf"},
    )


# CSV Export
@router.get("/summary/csv")
async def export_summary_csv(start: str, end: str):
    try:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
    except:
        raise HTTPException(status_code=400, detail="Invalid date format")

    data = await run_summary_pipeline(start_date, end_date)

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["vendor_id", "status", "total_orders", "total_amount"])

    # Data rows
    for row in data:
        writer.writerow(
            [
                row["vendor_id"],
                row["status"],
                row["total_orders"],
                f"{row['total_amount']:.2f}",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=summary.csv"},
    )
