import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ruido Message - Audio Steganography",
  description: "Encode and decode hidden messages in audio files using Huffman compression and RSA encryption",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-white">{children}</body>
    </html>
  );
}
