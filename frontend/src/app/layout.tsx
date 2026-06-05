import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Robot Framework AI Assistant",
  description: "AI-driven automation for Robot Framework - Generate test data, explore environments, create test cases, and more",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
