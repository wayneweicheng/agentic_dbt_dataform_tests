import { NextResponse } from "next/server";

export async function POST() {
  const serviceUrl = process.env.SDK_SERVICE_URL;
  if (!serviceUrl) {
    return NextResponse.json({ error: "SDK_SERVICE_URL is not configured" }, { status: 500 });
  }

  const response = await fetch(`${serviceUrl}/run-workflow`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tech_spec_path: "tech_specs/order_revenue_mart.md",
      validation_mode: "local",
      user_notes: "Triggered from the Next.js lab frontend."
    })
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
