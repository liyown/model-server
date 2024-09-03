import { createContext } from "react";

interface UserInfo {
  userName: string;
  role: string;
}

interface GlobalContext {
  userInfo: UserInfo;
  setUserInfo: (userInfo: UserInfo) => void;
}

const globalContext = createContext<GlobalContext>({} as GlobalContext);

export default globalContext;