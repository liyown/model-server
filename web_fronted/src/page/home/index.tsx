import { Avatar, Button, Layout } from "@arco-design/web-react";
import { Suspense, useContext } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Globalhead from "@/component/globalhead";
import { routes } from "@/router";
import GlobalContext from "@/context";
import { IconClose } from "@arco-design/web-react/icon";

const Header = Layout.Header;
const Footer = Layout.Footer;
const Content = Layout.Content;

function Index() {
  const navigate = useNavigate();
  const { userInfo, setUserInfo } = useContext(GlobalContext);
  return (
    <>
      <Layout className="h-screen">
        <Header className="shadow-sm">
          <Globalhead routes={routes} child={"home"}>
            {userInfo.role === "NO_LOGIN" ? (
              <Button
                size={"mini"}
                shape={"round"}
                type="outline"
                onClick={() => {
                  navigate("/login");
                }}
              >
                登录
              </Button>
            ) : (
              <>
                <Avatar
                  triggerIcon={<IconClose />}
                  triggerType="mask"
                  onClick={() => {
                    navigate("/login");
                    setUserInfo({ userName: "", role: "NO_LOGIN" });
                  }}
                >
                  {userInfo.userName}
                </Avatar>
              </>
            )}
          </Globalhead>
        </Header>
        <Content>
          <Suspense fallback={<div>router loading...</div>}>
            <Outlet />
          </Suspense>
        </Content>
        <Footer className="mx-auto font-mono font-bold">
          Design by Liuyaowen
        </Footer>
      </Layout>
    </>
  );
}

export default Index;
