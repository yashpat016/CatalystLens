/** @type {import('next').NextConfig} */
const apiUpstream =
  process.env.API_BASE_URL_INTERNAL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // We use the App Router; nothing experimental required for Sprint 1.
  },
  // Allow the dev server inside Docker to be reached from the host on any IP.
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${apiUpstream}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
