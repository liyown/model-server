import router from "./router";
import { RouterProvider } from "react-router-dom";
import GlobalContext from "./context";
import { useEffect, useState } from "react";
import { Permission } from "@/component/PermissionWrapper";
import Loading from "@/component/Loading";

export interface UserInfo {
  userName: string;
  role: string;
}

function App() {
  const [userInfo, setUserInfo] = useState<UserInfo>({
    userName: "admin",
    role: Permission.NO_LOGIN
  });

  useEffect(() => {
    // 从 localStorage 中获取 token
    const token = localStorage.getItem("token");
    console.log("token", token);
    if (token) {
      try {
        setUserInfo({
          userName: "admin",
          role: Permission.ADMIN
        })

      } catch (error) {
        console.error("Invalid token:", error);
      }
    } else {
      console.log("No token found");
    }
  }, []);


  return (
    <GlobalContext.Provider value={{ userInfo, setUserInfo }}>
      <RouterProvider
        router={router}
        fallbackElement={<Loading />}
      ></RouterProvider>
    </GlobalContext.Provider>
  );
}

export default App;
