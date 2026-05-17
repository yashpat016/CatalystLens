import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CatalystLens',
  description: 'Market event and liquidity intelligence dashboard.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-bg font-sans text-text antialiased">{children}</body>
    </html>
  );
}
