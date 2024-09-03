import { Route } from "@/router";

export function getChildRoutes(routes: Route[], id: string) {
  return routes.filter((route) => route.id === id).pop()?.children || [];
}
