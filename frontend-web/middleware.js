import { NextResponse } from "next/server";

export function middleware(request) {
  const token = request.cookies.get("access")?.value;
  const { pathname } = request.nextUrl;

  const publicRoutes = ["/login", "/signup", "/verify-otp"];

  // Allow public pges
  if (publicRoutes.includes(pathname)) {
    if (token) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}
