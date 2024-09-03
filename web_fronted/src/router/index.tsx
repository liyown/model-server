import { createBrowserRouter, Navigate } from "react-router-dom";
import Home from "../page/home/index.tsx";
import { RouteObject } from "react-router/dist/lib/context";
import { Permission } from "@/component/PermissionWrapper";
import ErrorPage from "@/page/home/ErrorPage";

export type Route = RouteObject & {
  id?: string;
  title?: string;
  children?: Route[];
  meta?: RouteMeta;
};

interface RouteMeta {
  showHeader?: boolean;
  needPermission?: Permission;
}

export const routes: Route[] = [
  {
    id: "home",
    title: "首页",
    path: "/",
    element: <Home />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        meta: {
          showHeader: false,
        },
        element: <Navigate to={"/welcome"} />,
      },
      {
        id: "welcome",
        title: "欢迎",
        path: "/welcome",
        lazy: () => import("../page/home/welcome"),
      },
      {
        id: "APIToken管理",
        title: "APIToken管理",
        path: "/token_manager",
        lazy: () => import("../page/home/token_manager"),
      },
      {
        id: "系统监控",
        title: "系统监控",
        path: "/monitor",
        lazy: () => import("../page/home/monitor"),
      },
      {
        id: "login",
        title: "登录",
        path: "/login",
        meta: { showHeader: false },
        lazy: () => import("../page/home/userlogin"),
      }
    ],
  },
];
const router = createBrowserRouter(routes, {
  basename: "/admin",
})
export default router;
