import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const PUBLIC_ROUTES = ["/auth"];

const ROLE_ROUTES: Record<string, string[]> = {
  operator: ["/operator"],
  driver:   ["/driver"],
  admin:    ["/admin"],
};

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Always allow public routes
  if (PUBLIC_ROUTES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next();
  }

  // Read auth state from cookie (set by client after login)
  const token = request.cookies.get("access_token")?.value;
  const role  = request.cookies.get("user_role")?.value;

  if (!token) {
    return NextResponse.redirect(new URL("/auth", request.url));
  }

  // Role-based protection
  for (const [requiredRole, paths] of Object.entries(ROLE_ROUTES)) {
    if (paths.some((p) => pathname.startsWith(p)) && role !== requiredRole && role !== "admin") {
      return NextResponse.redirect(new URL("/search", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|manifest.json|icons).*)"],
};
