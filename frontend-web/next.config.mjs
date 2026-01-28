/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "https://cartsy-ht0x.onrender.com/",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;
