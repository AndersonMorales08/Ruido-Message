import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const formData = await request.formData();
  const encoderUrl = process.env.ENCODER_URL || 'http://localhost:8000';
  
  const response = await fetch(`${encoderUrl}/encode`, {
    method: 'POST',
    body: formData,
  });

  const buffer = await response.arrayBuffer();
  return new NextResponse(buffer, {
    headers: { 'Content-Type': 'audio/wav', 'Content-Disposition': 'attachment; filename="encoded.wav"' },
  });
}