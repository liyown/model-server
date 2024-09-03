import React, { useContext } from "react";
import GlobalContext from "@/context";
import { useNavigate } from "react-router-dom";
import { UserInfo } from "@/App.tsx";

export enum Permission {
  ADMIN = "ADMIN",
  USER = "USER",
  NO_LOGIN = "NO_LOGIN",
}

export function checkPermission(
  needPermission: Permission,
  userInfo: UserInfo,
) {
  if (userInfo.role === Permission.ADMIN) {
    return true;
  } else if (userInfo.role === Permission.USER) {
    return needPermission === Permission.USER;
  } else {
    return false;
  }
}

interface PermissionWrapperProps {
  needPermission: Permission;
  children: React.ReactNode;
}

export default ({ needPermission, children }: PermissionWrapperProps) => {
  // todo 权限控制

  const { userInfo } = useContext(GlobalContext);
  const navigate = useNavigate();
  if (userInfo.role === Permission.ADMIN) {
    navigate("/login");
  }
  return <div>{checkPermission(needPermission, userInfo) && children}</div>;
};
