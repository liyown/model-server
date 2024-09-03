import { Button, Form, Input, Message } from "@arco-design/web-react";
import Password from "@arco-design/web-react/es/Input/password";
import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import GlobalContext from "@/context";
import instant from "@/axios";

const FormItem = Form.Item;

export function Component() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const globalContext = useContext(GlobalContext);
  return (
    <Form
      form={form}
      style={{ width: 600 }}
      className="mx-auto mt-32"
      autoComplete="off"
      onSubmit={(v) => {
        instant.post("/login", v).then((res) => {
          if (res.status === 200) {
            console.log("Login successfully:", res.data);
            globalContext.setUserInfo(res.data);
            navigate("/");
          }
        }).catch((error) => {
          if (error.response) {
            const statusCode = error.response.status;

            if (statusCode === 401) {
              // 401 未登录，跳转到登录页面
              Message.error("账号密码错误");
            } else {
              // 处理其他状态码
              console.error(`An error occurred: HTTP ${statusCode}`, error);
            }
          } else {
            // 处理没有响应的错误
            console.error("An error occurred:", error);
          }

        });
      }}

    >
      <FormItem
        label="用户名"
        field="username"
        rules={[
          { required: true },
          { match: /^[a-zA-Z0-9]{3,}$/, message: "用户名必须是6位以上" }
        ]}
      >
        <Input placeholder="输入用户名" />
      </FormItem>
      <FormItem
        label="密码"
        field="password"
        rules={[
          { required: true, type: "string" },
          { match: /^[a-zA-Z0-9]{3,}$/, message: "密码必须是6位以上" }
        ]}
      >
        <Password placeholder="输入密码" />
      </FormItem>
      <FormItem wrapperCol={{ offset: 5 }}>
        <Button type="primary" htmlType="submit" style={{ marginRight: 4 }}>
          登录
        </Button>
        <Button
          style={{ marginRight: 24 }}
          onClick={() => {
            form.resetFields();
          }}
        >
          Reset
        </Button>
      </FormItem>
    </Form>
  );
}
