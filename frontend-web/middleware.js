import { NextResponse } from "next/server";

export function middleware(request) {
  const token = request.cookies.get("access")?.value;
  const { pathname } = request.nextUrl;

  const publicRoutes = ["/login", "/signup", "/verify-otp"];

  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon") ||
    pathname.startsWith("/api")
  ) {
    return NextResponse.next();
  }

  if (!token && !publicRoutes.includes(pathname)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (token && publicRoutes.includes(pathname)) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}
