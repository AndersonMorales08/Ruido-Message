import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const formData = await request.formData();
  const decoderUrl = process.env.DECODER_URL || 'http://localhost:8001';
  
  const response = await fetch(`${decoderUrl}/decode`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();
  return NextResponse.json(data);
}