import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Removed hardcoded turbopack.root - let Next.js auto-detect project root
  experimental: {
    // Allow large file uploads up to 500MB (using new property name)
    proxyClientMaxBodySize: '500mb',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
};

export default nextConfig;
