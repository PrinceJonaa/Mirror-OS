import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: '/Users/princejona/a1/dashboard/frontend',
  },
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
