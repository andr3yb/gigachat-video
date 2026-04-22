/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Allow using the frontend directly on :3000 while still hitting backend API.
    // In Docker, `backend` is resolvable by service name.
    const apiTarget = process.env.NEXT_INTERNAL_API_URL || "http://backend:8000/api";
    return [
      {
        source: "/api/:path*",
        destination: `${apiTarget}/:path*`
      }
    ];
  }
};

module.exports = nextConfig;
