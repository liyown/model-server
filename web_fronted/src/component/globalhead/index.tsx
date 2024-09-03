import "@arco-design/web-react/dist/css/arco.css";
import "./index.css";
import Logo from "@/assets/logo.svg";
import { Grid, Menu } from "@arco-design/web-react";
import { Route } from "@/router";
import { useLocation, useNavigate } from "react-router-dom";
import React from "react";
import { getChildRoutes } from "@/utils";
import { checkPermission } from "@/component/PermissionWrapper";
import { UserInfo } from "@/App.tsx";
import GlobalContext from "@/context";

const Row = Grid.Row;
const Col = Grid.Col;

const MenuItem = Menu.Item;
const SubMenu = Menu.SubMenu;

function generateMenu(routes: Route[], userInfo: UserInfo) {
  return routes.map((route) => {
    if (route.meta && route.meta.showHeader === false) {
      return null;
    }
    if (route.meta && route.meta.needPermission) {
      if (!checkPermission(route.meta.needPermission, userInfo)) {
        return null;
      }
    }
    if (route.children) {
      return (
        <SubMenu key={route.path as string} title={route.title}>
          {generateMenu(route.children, userInfo)}
        </SubMenu>
      );
    }
    return (
      <MenuItem className="font-bold" key={route.path as string}>
        {route.title}
      </MenuItem>
    );
  });
}
interface AppProps {
  routes: Route[];
  child: string;
  children?: React.ReactNode;
}

function App({ routes, child, children }: AppProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { userInfo } = React.useContext(GlobalContext);
  const handelClickMenu = (key: string) => {
    navigate(key);
  };
  return (
    <div>
      <Row className=" items-center justify-center ">
        <Col flex="auto">
          <Menu
            selectedKeys={[location.pathname]}
            onClickMenuItem={handelClickMenu}
            mode="horizontal"
            defaultSelectedKeys={["welcome"]}
          >
            <MenuItem key="0" style={{ padding: 0, marginRight: 16 }} disabled>
              <div>
                <img src={Logo} alt="logo" style={{ width: 48, height: 48 }} />
              </div>
            </MenuItem>
            {generateMenu(getChildRoutes(routes, child), userInfo)}
          </Menu>
        </Col>
        <Col flex="100px">{children}</Col>
      </Row>
    </div>
  );
}

export default App;
