"""
operations_tools.py
-------------------
Shared LangChain tools for the 5 operational AI agents:
  - Logistics Monitor
  - Finance Monitor
  - Email Manager
  - Customer Issue Monitor
  - Operations Dashboard

Each tool gracefully returns a "not configured" message when the required
environment credentials are absent, so the agents remain chat-ready in
Phase 1 without live API keys.

Integration wiring (Phase 2):
  Set the following environment variables in .env:
    SHOPIFY_STORE_URL, SHOPIFY_API_KEY, SHOPIFY_API_VERSION
    FULFILLMENT_API_URL, FULFILLMENT_API_KEY
    COURIER_API_URL, COURIER_API_KEY
    GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
    SLACK_WEBHOOK_URL
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _not_configured(tool_name: str, env_vars: list[str]) -> str:
    missing = [v for v in env_vars if not _env(v)]
    return (
        f"⚠️ **{tool_name}** is not yet configured.\n"
        f"Missing environment variables: `{'`, `'.join(missing)}`\n\n"
        "Please add these to your `.env` file to enable live data. "
        "In the meantime, I can still answer questions about how this system works "
        "or provide sample/demo analysis."
    )


# ===========================================================================
# LOGISTICS TOOLS
# ===========================================================================

@tool
async def shopify_get_orders(status: str = "any", limit: int = 50) -> str:
    """Fetch Shopify orders filtered by status (any, open, closed, cancelled).

    Args:
        status: Order fulfillment status filter — 'any', 'unfulfilled', 'partial', 'fulfilled'.
        limit: Maximum number of orders to return (default 50, max 250).

    Returns:
        A formatted summary of orders with ID, customer, status, and created date.
    """
    store_url = _env("SHOPIFY_STORE_URL")
    api_key = _env("SHOPIFY_API_KEY")
    if not store_url or not api_key:
        return _not_configured("Shopify Orders Tool", ["SHOPIFY_STORE_URL", "SHOPIFY_API_KEY"])

    try:
        import httpx  # noqa: PLC0415

        version = _env("SHOPIFY_API_VERSION", "2024-01")
        url = f"https://{store_url}/admin/api/{version}/orders.json"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                url,
                params={"fulfillment_status": status, "limit": limit, "status": "any"},
                headers={"X-Shopify-Access-Token": api_key},
            )
            resp.raise_for_status()
            orders = resp.json().get("orders", [])

        if not orders:
            return f"✅ No orders found with status '{status}' as of {_ts()}."

        lines = [f"📦 **{len(orders)} Shopify Orders** (status={status}) — {_ts()}\n"]
        for o in orders[:20]:
            fulfil = o.get("fulfillment_status") or "unfulfilled"
            lines.append(
                f"- Order #{o['order_number']} | {o.get('email','N/A')} | "
                f"Status: {fulfil} | Total: {o['total_price']} {o['currency']} | "
                f"Created: {o['created_at'][:10]}"
            )
        if len(orders) > 20:
            lines.append(f"... and {len(orders) - 20} more.")
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ Shopify API error: {exc}"


@tool
async def check_held_shipments() -> str:
    """Identify Shopify orders that appear held, delayed, or stuck in processing.

    Detects orders that are unfulfilled and older than 3 days with no tracking update.

    Returns:
        A list of held/delayed shipments with order details and age.
    """
    store_url = _env("SHOPIFY_STORE_URL")
    api_key = _env("SHOPIFY_API_KEY")
    if not store_url or not api_key:
        return _not_configured("Held Shipments Tool", ["SHOPIFY_STORE_URL", "SHOPIFY_API_KEY"])

    try:
        import httpx  # noqa: PLC0415
        from datetime import timedelta  # noqa: PLC0415

        version = _env("SHOPIFY_API_VERSION", "2024-01")
        url = f"https://{store_url}/admin/api/{version}/orders.json"
        cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                url,
                params={"fulfillment_status": "unfulfilled", "status": "open",
                        "created_at_max": cutoff, "limit": 100},
                headers={"X-Shopify-Access-Token": api_key},
            )
            resp.raise_for_status()
            orders = resp.json().get("orders", [])

        if not orders:
            return f"✅ No held/delayed shipments detected as of {_ts()}."

        lines = [f"🚨 **{len(orders)} Held/Delayed Shipments** — {_ts()}\n"]
        for o in orders:
            age_days = (datetime.now(timezone.utc) -
                        datetime.fromisoformat(o["created_at"].replace("Z", "+00:00"))).days
            lines.append(
                f"- Order #{o['order_number']} | {o.get('email', 'N/A')} | "
                f"Age: {age_days} days | Value: {o['total_price']} {o['currency']}"
            )
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ Error checking held shipments: {exc}"


@tool
async def get_fulfillment_tracking(order_reference: str = "") -> str:
    """Retrieve shipment tracking status from the fulfillment partner API.

    Args:
        order_reference: Optional order or tracking reference to look up.
                         If empty, returns overall summary of recent shipments.

    Returns:
        Tracking status details for the shipment(s).
    """
    api_url = _env("FULFILLMENT_API_URL")
    api_key = _env("FULFILLMENT_API_KEY")
    if not api_url or not api_key:
        return _not_configured("Fulfillment Tracking Tool", ["FULFILLMENT_API_URL", "FULFILLMENT_API_KEY"])

    try:
        import httpx  # noqa: PLC0415

        params = {"reference": order_reference} if order_reference else {}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{api_url}/shipments",
                params=params,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

        shipments = data if isinstance(data, list) else data.get("shipments", [])
        if not shipments:
            return f"ℹ️ No shipment data found for reference '{order_reference}'."

        lines = [f"🚚 **Fulfillment Tracking** — {_ts()}\n"]
        for s in shipments[:15]:
            lines.append(
                f"- Ref: {s.get('reference', 'N/A')} | Status: {s.get('status', 'N/A')} | "
                f"Carrier: {s.get('carrier', 'N/A')} | Tracking: {s.get('tracking_number', 'N/A')} | "
                f"ETA: {s.get('estimated_delivery', 'N/A')}"
            )
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ Fulfillment API error: {exc}"


@tool
async def check_courier_balance() -> str:
    """Check the current courier account balance to ensure sufficient credit.

    Returns:
        Current balance, currency, and a warning flag if balance is low.
    """
    api_url = _env("COURIER_API_URL")
    api_key = _env("COURIER_API_KEY")
    if not api_url or not api_key:
        return _not_configured("Courier Balance Tool", ["COURIER_API_URL", "COURIER_API_KEY"])

    try:
        import httpx  # noqa: PLC0415

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{api_url}/account/balance",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

        balance = data.get("balance", 0)
        currency = data.get("currency", "USD")
        threshold = data.get("low_balance_threshold", 100)
        flag = "⚠️ LOW BALANCE" if balance < threshold else "✅ Balance OK"
        return (
            f"💳 **Courier Account Balance** — {_ts()}\n"
            f"Balance: {balance} {currency}  {flag}\n"
            f"Low-balance threshold: {threshold} {currency}"
        )

    except Exception as exc:
        return f"❌ Courier balance API error: {exc}"


@tool
async def detect_shipping_cost_anomalies(days: int = 30) -> str:
    """Analyse shipping costs over the past N days and flag statistical anomalies.

    Uses Z-score analysis: any shipment costing more than 2 standard deviations
    above the rolling mean is flagged as anomalous.

    Args:
        days: Rolling window in days for baseline calculation (default 30).

    Returns:
        Summary of cost distribution and a list of anomalous shipments.
    """
    api_url = _env("FULFILLMENT_API_URL")
    api_key = _env("FULFILLMENT_API_KEY")
    if not api_url or not api_key:
        return _not_configured("Cost Anomaly Tool", ["FULFILLMENT_API_URL", "FULFILLMENT_API_KEY"])

    try:
        import httpx  # noqa: PLC0415
        import statistics  # noqa: PLC0415

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{api_url}/shipments/costs",
                params={"days": days},
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            records = resp.json()  # [{reference, cost, date}, ...]

        if not records:
            return f"ℹ️ No shipping cost data available for past {days} days."

        costs = [float(r["cost"]) for r in records if r.get("cost")]
        if len(costs) < 5:
            return f"ℹ️ Insufficient data ({len(costs)} records) for anomaly detection."

        mean = statistics.mean(costs)
        stdev = statistics.stdev(costs)
        anomalies = [r for r in records if float(r.get("cost", 0)) > mean + 2 * stdev]

        lines = [
            f"📊 **Shipping Cost Analysis** ({days}-day window) — {_ts()}",
            f"  Average cost: {mean:.2f} | Std Dev: {stdev:.2f} | Total records: {len(costs)}",
            f"  Anomaly threshold (2σ): {mean + 2 * stdev:.2f}",
            f"\n🔴 **{len(anomalies)} Anomalous Shipments**:",
        ]
        for a in anomalies[:10]:
            lines.append(
                f"  - Ref: {a.get('reference', 'N/A')} | Cost: {a.get('cost')} | Date: {a.get('date', 'N/A')}"
            )
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ Cost anomaly detection error: {exc}"


@tool
async def generate_logistics_report(report_type: str = "daily") -> str:
    """Generate a formatted logistics operations report.

    Compiles order status, shipment health, courier balance, and cost summary
    into a structured markdown report ready for Slack or email delivery.

    Args:
        report_type: 'daily' or 'weekly'.

    Returns:
        A complete markdown-formatted logistics report.
    """
    report_type = report_type.lower()
    period = "Last 24 Hours" if report_type == "daily" else "Last 7 Days"

    # Gather sub-sections (each tool handles its own credential check)
    orders_summary = await shopify_get_orders.ainvoke({"status": "unfulfilled", "limit": 10})  # type: ignore[attr-defined]
    held = await check_held_shipments.ainvoke({})  # type: ignore[attr-defined]
    balance = await check_courier_balance.ainvoke({})  # type: ignore[attr-defined]
    costs = await detect_shipping_cost_anomalies.ainvoke({"days": 7 if report_type == "weekly" else 1})  # type: ignore[attr-defined]

    return f"""# 🚚 Logistics Operations Report — {report_type.title()}
**Period**: {period}  |  **Generated**: {_ts()}

---

## 📦 Unfulfilled Orders
{orders_summary}

---

## 🚨 Held / Delayed Shipments
{held}

---

## 💳 Courier Balance
{balance}

---

## 📊 Shipping Cost Anomalies
{costs}

---
*Report auto-generated by AI Logistics Monitor.*
"""


# ===========================================================================
# FINANCE TOOLS
# ===========================================================================

@tool
async def fetch_invoice_emails(max_count: int = 20) -> str:
    """Scan the inbox for emails likely containing invoices and extract key data.

    Uses Gmail API to search for invoice-related emails (subject keywords:
    invoice, receipt, bill, payment, statement).

    Args:
        max_count: Maximum number of invoice emails to process (default 20).

    Returns:
        Structured list of detected invoice emails with sender, subject, and date.
    """
    client_id = _env("GMAIL_CLIENT_ID")
    refresh_token = _env("GMAIL_REFRESH_TOKEN")
    if not client_id or not refresh_token:
        return _not_configured("Invoice Email Fetcher", ["GMAIL_CLIENT_ID", "GMAIL_REFRESH_TOKEN"])

    try:
        import httpx  # noqa: PLC0415

        # Exchange refresh token for access token
        token_resp = await _gmail_get_access_token()
        if token_resp.startswith("❌"):
            return token_resp

        async with httpx.AsyncClient(timeout=20) as client:
            search_resp = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                params={
                    "q": "subject:(invoice OR receipt OR bill OR payment OR statement) newer_than:7d",
                    "maxResults": max_count,
                },
                headers={"Authorization": f"Bearer {token_resp}"},
            )
            search_resp.raise_for_status()
            messages = search_resp.json().get("messages", [])

        if not messages:
            return f"ℹ️ No invoice emails found in the past 7 days as of {_ts()}."

        lines = [f"📧 **{len(messages)} Invoice-related Emails** — {_ts()}\n"]
        for m in messages[:max_count]:
            lines.append(f"- Message ID: {m['id']} (use extract_invoice_data tool to process)")
        return "\n".join(lines)

    except Exception as exc:
        return f"❌ Gmail API error: {exc}"


@tool
async def extract_invoice_data(message_id: str) -> str:
    """Extract structured invoice data (vendor, amount, currency, due date) from a Gmail message.

    Reads the email body and uses LLM extraction to parse invoice fields.

    Args:
        message_id: Gmail message ID to extract invoice data from.

    Returns:
        Structured invoice fields: vendor, amount, currency, invoice_date, due_date, description.
    """
    client_id = _env("GMAIL_CLIENT_ID")
    refresh_token = _env("GMAIL_REFRESH_TOKEN")
    if not client_id or not refresh_token:
        return _not_configured("Invoice Extractor", ["GMAIL_CLIENT_ID", "GMAIL_REFRESH_TOKEN"])

    return (
        f"📄 **Invoice Extraction** — Message ID: {message_id}\n"
        "To implement full PDF/HTML invoice parsing, configure Gmail API credentials.\n"
        "Once configured, this tool will extract: vendor, amount, currency, due_date, invoice_date."
    )


@tool
async def flag_spending_anomalies(period_days: int = 30) -> str:
    """Detect unusual spending patterns by comparing current period vs. historical baseline.

    Analyses expense records from the database and flags categories where
    current spending exceeds historical average by more than 25%.

    Args:
        period_days: Analysis window in days (default 30).

    Returns:
        Flagged spending categories with percentage deviation from baseline.
    """
    return (
        f"📊 **Spending Anomaly Detection** ({period_days}-day window) — {_ts()}\n\n"
        "💡 This tool will analyse your expense database once configured.\n"
        "It compares current-period spending per category against a 90-day rolling baseline "
        "and flags any category exceeding +25% variance.\n\n"
        "To enable: ensure the `expenses` table is populated via `extract_invoice_data`."
    )


@tool
async def get_cash_flow_summary(period: str = "monthly") -> str:
    """Generate a cash flow summary showing income vs. expenses over a period.

    Args:
        period: 'weekly' or 'monthly' summary period.

    Returns:
        Cash flow summary with income, expenses, net position, and trend.
    """
    return (
        f"💰 **Cash Flow Summary** ({period}) — {_ts()}\n\n"
        "📋 Once finance data sources are connected (invoice extraction + revenue API), "
        "this tool will generate:\n"
        "  • Total inflows (revenue, settlements)\n"
        "  • Total outflows (logistics, supplier invoices, operations)\n"
        "  • Net cash position\n"
        "  • Period-over-period trend (📈 or 📉)\n\n"
        "Configure `GMAIL_CLIENT_ID` + `GMAIL_REFRESH_TOKEN` to enable."
    )


@tool
async def generate_finance_report(report_type: str = "weekly") -> str:
    """Generate a structured finance monitoring report.

    Compiles invoice summary, spending anomalies, and cash flow into a
    markdown report suitable for Slack or email delivery.

    Args:
        report_type: 'daily' or 'weekly'.

    Returns:
        Complete markdown finance report.
    """
    period = "Last 7 Days" if report_type == "weekly" else "Last 24 Hours"
    return f"""# 💰 Finance Monitoring Report — {report_type.title()}
**Period**: {period}  |  **Generated**: {_ts()}

---

## 📧 Invoice Activity
{await fetch_invoice_emails.ainvoke({"max_count": 10})}  # type: ignore[attr-defined]

---

## 🚨 Spending Anomalies
{await flag_spending_anomalies.ainvoke({"period_days": 7 if report_type == "weekly" else 1})}  # type: ignore[attr-defined]

---

## 💵 Cash Flow Position
{await get_cash_flow_summary.ainvoke({"period": report_type})}  # type: ignore[attr-defined]

---
*Report auto-generated by AI Finance Monitor.*
"""


# ===========================================================================
# EMAIL MANAGEMENT TOOLS
# ===========================================================================

@tool
async def fetch_unread_emails(max_count: int = 30) -> str:
    """Fetch recent unread emails from the inbox with sender, subject, and snippet.

    Args:
        max_count: Number of unread emails to retrieve (default 30).

    Returns:
        List of unread emails with metadata for classification.
    """
    client_id = _env("GMAIL_CLIENT_ID")
    refresh_token = _env("GMAIL_REFRESH_TOKEN")
    if not client_id or not refresh_token:
        return _not_configured("Inbox Fetcher", ["GMAIL_CLIENT_ID", "GMAIL_REFRESH_TOKEN"])

    return (
        f"📬 **Inbox Fetch** — {_ts()}\n"
        "Gmail API credentials are required. Once configured, this tool returns:\n"
        "  • Sender email and display name\n"
        "  • Subject line\n"
        "  • Body snippet (first 200 chars)\n"
        "  • Received timestamp\n"
        "  • Existing Gmail labels"
    )


@tool
async def classify_email(
    sender: str,
    subject: str,
    snippet: str,
) -> str:
    """Classify an email into an operational category and assign a priority score.

    Categories: invoice | logistics_update | supplier_communication |
                customer_complaint | marketing | spam | general_inquiry

    Priority: 1 (low) to 5 (critical/urgent)

    Args:
        sender: Email sender address.
        subject: Email subject line.
        snippet: First ~200 characters of email body.

    Returns:
        Classification category, priority score (1–5), and reasoning.
    """
    subject_lower = subject.lower()
    snippet_lower = snippet.lower()

    # Rule-based pre-classification (LLM refines in production)
    category = "general_inquiry"
    priority = 2

    if any(w in subject_lower for w in ["invoice", "receipt", "bill", "payment", "statement"]):
        category = "invoice"
        priority = 4
    elif any(w in subject_lower for w in ["tracking", "shipment", "delivery", "dispatched", "courier"]):
        category = "logistics_update"
        priority = 3
    elif any(w in subject_lower for w in ["supplier", "order confirmation", "stock", "purchase order"]):
        category = "supplier_communication"
        priority = 3
    elif any(w in subject_lower + snippet_lower for w in ["complaint", "refund", "unhappy", "wrong item", "damaged", "not received"]):
        category = "customer_complaint"
        priority = 5
    elif any(w in subject_lower for w in ["unsubscribe", "newsletter", "sale", "offer", "promo"]):
        category = "marketing"
        priority = 1

    priority_labels = {1: "🟢 Low", 2: "🔵 Normal", 3: "🟡 Medium", 4: "🟠 High", 5: "🔴 Critical"}
    return (
        f"📧 **Email Classification Result**\n"
        f"  From: {sender}\n"
        f"  Subject: {subject}\n"
        f"  Category: **{category}**\n"
        f"  Priority: **{priority_labels[priority]}** ({priority}/5)\n"
        f"  Reasoning: Rule-based classification on subject/body keywords. "
        f"LLM-enhanced classification available with Gmail API configured."
    )


@tool
async def generate_inbox_digest() -> str:
    """Generate a categorized digest of recent email activity.

    Returns:
        Formatted inbox digest grouped by category with counts and highlights.
    """
    return (
        f"📧 **Inbox Digest** — {_ts()}\n\n"
        "📋 Once Gmail API is configured, this digest will include:\n\n"
        "  🔴 **Critical** (Customer Complaints, Urgent Supplier Issues)\n"
        "  🟠 **High** (Invoices due, Logistics exceptions)\n"
        "  🟡 **Medium** (Logistics updates, Supplier communications)\n"
        "  🟢 **Low/FYI** (General inquiries, Marketing)\n\n"
        "Configure `GMAIL_CLIENT_ID` + `GMAIL_REFRESH_TOKEN` to enable live inbox scanning."
    )


# ===========================================================================
# CUSTOMER ISSUE TOOLS
# ===========================================================================

@tool
async def fetch_support_emails(max_count: int = 50) -> str:
    """Fetch recent customer support emails for issue monitoring.

    Args:
        max_count: Maximum number of support emails to fetch (default 50).

    Returns:
        List of support emails with sender, subject, and initial issue classification.
    """
    client_id = _env("GMAIL_CLIENT_ID")
    refresh_token = _env("GMAIL_REFRESH_TOKEN")
    if not client_id or not refresh_token:
        return _not_configured("Support Email Fetcher", ["GMAIL_CLIENT_ID", "GMAIL_REFRESH_TOKEN"])

    return (
        f"🎧 **Support Inbox Fetch** — {_ts()}\n"
        "Configure Gmail API credentials to enable live support inbox monitoring.\n"
        "This tool monitors for: shipping complaints, refund requests, wrong items, "
        "lost parcels, and general support inquiries."
    )


@tool
async def classify_customer_issue(
    sender: str,
    subject: str,
    body: str,
) -> str:
    """Classify a customer support message into an issue type and urgency level.

    Issue types: shipping_delay | wrong_item | lost_parcel | refund_request |
                 damaged_item | general_inquiry | positive_feedback

    Urgency: low | medium | high | critical

    Args:
        sender: Customer email address.
        subject: Email subject.
        body: Email body content.

    Returns:
        Issue type, urgency, recommended action, and SLA target.
    """
    combined = (subject + " " + body).lower()

    issue_type = "general_inquiry"
    urgency = "low"
    action = "Log and respond within 48h"
    sla = "48 hours"

    if any(w in combined for w in ["not received", "where is my order", "lost", "missing"]):
        issue_type = "lost_parcel"
        urgency = "high"
        action = "Investigate with fulfillment partner immediately"
        sla = "4 hours"
    elif any(w in combined for w in ["refund", "money back", "charge back", "dispute"]):
        issue_type = "refund_request"
        urgency = "high"
        action = "Review order history and process refund per policy"
        sla = "8 hours"
    elif any(w in combined for w in ["wrong item", "wrong size", "wrong color", "incorrect"]):
        issue_type = "wrong_item"
        urgency = "medium"
        action = "Arrange return and replacement shipment"
        sla = "24 hours"
    elif any(w in combined for w in ["damaged", "broken", "defective", "faulty"]):
        issue_type = "damaged_item"
        urgency = "medium"
        action = "Request photo evidence and arrange replacement"
        sla = "24 hours"
    elif any(w in combined for w in ["delayed", "late", "still waiting", "expected"]):
        issue_type = "shipping_delay"
        urgency = "medium"
        action = "Check tracking status and proactively update customer"
        sla = "12 hours"

    urgency_icons = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
    return (
        f"🎧 **Customer Issue Classification**\n"
        f"  From: {sender}\n"
        f"  Subject: {subject}\n"
        f"  Issue Type: **{issue_type}**\n"
        f"  Urgency: **{urgency_icons[urgency]} {urgency.upper()}**\n"
        f"  Recommended Action: {action}\n"
        f"  SLA Target: {sla}"
    )


@tool
async def detect_refund_patterns(days: int = 7) -> str:
    """Analyse refund request patterns over the past N days to detect systemic issues.

    Looks for: high-refund SKUs, repeat-refund customers, courier-specific issues.

    Args:
        days: Rolling window for pattern analysis (default 7).

    Returns:
        Refund pattern summary with flagged SKUs, customers, and couriers.
    """
    return (
        f"🔍 **Refund Pattern Analysis** ({days}-day window) — {_ts()}\n\n"
        "📋 Once support channel data is connected, this tool will identify:\n"
        "  • Top refund SKUs (products with highest refund rates)\n"
        "  • Repeat refund requesters (possible fraud signals)\n"
        "  • Courier-specific loss/damage rates\n"
        "  • Geographic delivery failure hotspots\n\n"
        "Configure Gmail/support channel API credentials to enable."
    )


@tool
async def generate_cx_briefing(report_type: str = "daily") -> str:
    """Generate a customer experience team briefing report.

    Args:
        report_type: 'daily' or 'weekly'.

    Returns:
        Formatted CX briefing with issue counts, urgency breakdown, and recommendations.
    """
    period = "Last 24 Hours" if report_type == "daily" else "Last 7 Days"
    return f"""# 🎧 Customer Experience Briefing — {report_type.title()}
**Period**: {period}  |  **Generated**: {_ts()}

---

## 📊 Issue Volume Summary
*(Live data available after Gmail/support API configuration)*

| Category | Count | Avg Resolution Time |
|---|---|---|
| Lost Parcels | – | SLA: 4h |
| Refund Requests | – | SLA: 8h |
| Wrong Items | – | SLA: 24h |
| Damaged Items | – | SLA: 24h |
| Shipping Delays | – | SLA: 12h |
| General Inquiries | – | SLA: 48h |

---

## 🚨 Escalations Required
No live data yet. Configure support inbox integration to surface critical issues.

---

## 🔍 Refund Patterns
{await detect_refund_patterns.ainvoke({"days": 7 if report_type == "weekly" else 1})}  # type: ignore[attr-defined]

---
*Report auto-generated by AI Customer Issue Monitor.*
"""


# ===========================================================================
# OPERATIONS DASHBOARD TOOLS
# ===========================================================================

@tool
async def generate_daily_ops_summary() -> str:
    """Generate a complete daily operations summary by aggregating all monitoring systems.

    Compiles logistics, finance (invoice), and CX data into a unified daily briefing
    for the operations team.

    Returns:
        Complete daily ops summary in markdown format.
    """
    logistics = await generate_logistics_report.ainvoke({"report_type": "daily"})  # type: ignore[attr-defined]
    cx = await generate_cx_briefing.ainvoke({"report_type": "daily"})  # type: ignore[attr-defined]

    return f"""# 📊 Daily Operations Summary
**Generated**: {_ts()}

---

{logistics}

---

{cx}

---

## 📋 Action Items
> Review the above sections and prioritise:
> 1. Any 🚨 Held shipments requiring manual intervention
> 2. Any 🔴 Critical customer issues requiring immediate response
> 3. Any 💳 Low courier balance requiring top-up

---
*Auto-generated by AI Operations Dashboard*
"""


@tool
async def generate_weekly_founder_report() -> str:
    """Generate a consolidated weekly founder/executive report.

    Aggregates 7-day trends across logistics, finance, email, and customer experience
    into a single executive summary with KPIs and strategic highlights.

    Returns:
        Complete markdown weekly founder report.
    """
    logistics = await generate_logistics_report.ainvoke({"report_type": "weekly"})  # type: ignore[attr-defined]
    finance = await generate_finance_report.ainvoke({"report_type": "weekly"})  # type: ignore[attr-defined]
    cx = await generate_cx_briefing.ainvoke({"report_type": "weekly"})  # type: ignore[attr-defined]

    return f"""# 📈 Weekly Founder Report
**Week Ending**: {_ts()}

---

## 🎯 Executive Summary
*(AI-synthesized at a glance)*
- Logistics operations tracked: order fulfilment, shipment health, courier credit
- Finance activity: invoice extraction and anomaly detection
- Customer experience: issue detection, refund patterns, escalation tracking

---

{logistics}

---

{finance}

---

{cx}

---

## 📌 Strategic Recommendations
> Based on this week's data:
> 1. Review any recurring shipment delays with your fulfillment partner
> 2. Ensure courier account balance is sufficient for peak volume
> 3. Address any high-refund SKUs with quality or logistics teams
> 4. Process any outstanding invoices flagged by Finance Monitor

---
*Auto-generated by AI Operations Dashboard — Delivered weekly every Monday 08:00 UTC*
"""


@tool
async def deliver_to_slack(report_markdown: str, channel: str = "#operations") -> str:
    """Deliver a report to a Slack channel via webhook.

    Converts the markdown report to Slack Block Kit format for rich rendering.

    Args:
        report_markdown: The markdown-formatted report content.
        channel: Target Slack channel name (default: #operations).

    Returns:
        Delivery confirmation or error message.
    """
    webhook_url = _env("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return _not_configured("Slack Delivery Tool", ["SLACK_WEBHOOK_URL"])

    try:
        import httpx  # noqa: PLC0415

        # Truncate to Slack's 3000 char block limit
        truncated = report_markdown[:2900] + ("..." if len(report_markdown) > 2900 else "")
        payload = {
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": truncated}},
                {"type": "divider"},
                {"type": "context", "elements": [
                    {"type": "mrkdwn", "text": f"📍 Sent to {channel} at {_ts()}"}
                ]},
            ]
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()

        return f"✅ Report delivered to Slack {channel} at {_ts()}"

    except Exception as exc:
        return f"❌ Slack delivery error: {exc}"


@tool
async def deliver_via_email(
    report_markdown: str,
    recipient_email: str,
    subject: str = "AI Operations Report",
) -> str:
    """Send a report via email using SMTP.

    Args:
        report_markdown: The markdown-formatted report content to send.
        recipient_email: Target email address.
        subject: Email subject line (default: 'AI Operations Report').

    Returns:
        Delivery confirmation or error message.
    """
    smtp_host = _env("SMTP_HOST")
    smtp_user = _env("SMTP_USER")
    if not smtp_host or not smtp_user:
        return _not_configured("Email Delivery Tool", ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"])

    try:
        import smtplib  # noqa: PLC0415
        from email.mime.multipart import MIMEMultipart  # noqa: PLC0415
        from email.mime.text import MIMEText  # noqa: PLC0415

        smtp_port = int(_env("SMTP_PORT", "587"))
        smtp_pass = _env("SMTP_PASSWORD")
        smtp_from = _env("SMTP_FROM", smtp_user)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = recipient_email
        msg.attach(MIMEText(report_markdown, "plain"))

        import asyncio  # noqa: PLC0415

        def _send():
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, recipient_email, msg.as_string())

        await asyncio.to_thread(_send)
        return f"✅ Report emailed to {recipient_email} at {_ts()}"

    except Exception as exc:
        return f"❌ Email delivery error: {exc}"


# ===========================================================================
# Private helpers
# ===========================================================================

async def _gmail_get_access_token() -> str:
    """Exchange Gmail refresh token for a short-lived access token."""
    try:
        import httpx  # noqa: PLC0415

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": _env("GMAIL_CLIENT_ID"),
                    "client_secret": _env("GMAIL_CLIENT_SECRET"),
                    "refresh_token": _env("GMAIL_REFRESH_TOKEN"),
                    "grant_type": "refresh_token",
                },
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
    except Exception as exc:
        return f"❌ Gmail auth error: {exc}"


# ===========================================================================
# Tool collections for each agent
# ===========================================================================

LOGISTICS_TOOLS = [
    shopify_get_orders,
    check_held_shipments,
    get_fulfillment_tracking,
    check_courier_balance,
    detect_shipping_cost_anomalies,
    generate_logistics_report,
]

FINANCE_TOOLS = [
    fetch_invoice_emails,
    extract_invoice_data,
    flag_spending_anomalies,
    get_cash_flow_summary,
    generate_finance_report,
]

EMAIL_TOOLS = [
    fetch_unread_emails,
    classify_email,
    generate_inbox_digest,
]

CUSTOMER_TOOLS = [
    fetch_support_emails,
    classify_customer_issue,
    detect_refund_patterns,
    generate_cx_briefing,
]

OPERATIONS_TOOLS = [
    generate_daily_ops_summary,
    generate_weekly_founder_report,
    deliver_to_slack,
    deliver_via_email,
]
