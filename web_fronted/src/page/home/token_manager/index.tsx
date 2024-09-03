import { Table, TableColumnProps, Button, Modal, Input, Message } from "@arco-design/web-react";
import { IconDelete, IconPlus } from "@arco-design/web-react/icon";
import { useEffect, useState } from "react";
import instant from "@/axios/index.ts";
import { useNavigate } from "react-router-dom";

interface TokenData {
  id: number;
  api_key: string;
  remark: string;

}

export function Component() {
  const [data, setData] = useState<TokenData[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [remark, setRemark] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    instant.get("/tokens")
      .then((res) => {
        console.log(document.cookie);
        if (res.status === 200) {
          // 正常处理返回的数据
          setData(res.data.data);
        }
      })
      .catch((error) => {
        if (error.response) {
          const statusCode = error.response.status;

          if (statusCode === 401) {
            // 401 未登录，跳转到登录页面
            Message.error("请先登录");
            navigate("/login");
          } else {
            // 处理其他状态码
            console.error(`An error occurred: HTTP ${statusCode}`, error);
          }
        } else {
          // 处理没有响应的错误
          Message.error("网络错误");
        }
      });
  }, [navigate]);

  const handleDelete = (apiKey: string) => {
    instant.delete(`/token/${apiKey}`);
    const filteredData = data?.filter(item => item.api_key !== apiKey);
    setData(filteredData);
  };

  const handleAdd = () => {
    if (!remark) {
      Message.error("请输入备注");
      return;
    }
    instant.post("/token", { remark }).then((res) => {
      setData([...data, res.data.data]);
      setIsModalVisible(false);
    });
  };

  const columns: TableColumnProps[] = [
    {
      title: "APIToken",
      dataIndex: "api_key"
    },
    {
      title: "备注",
      dataIndex: "remark"
    },
    {
      title: "操作",
      dataIndex: "actions",
      render: (_, record) => (
        <Button
          icon={<IconDelete />}
          onClick={() => handleDelete(record.api_key)}
          type="text"
          status="danger"
        >
          删除
        </Button>
      )
    }
  ];

  return (
    <>
      <div className="flex justify-end mr-6 mt-6">
        <Button
          icon={<IconPlus />}
          onClick={() => setIsModalVisible(true)}
          type="primary"
        >
          添加API
        </Button>
      </div>
      <div className="w-2/3 mx-auto h-screen mt-12">
        <h1>API Token Manager</h1>
        <Table columns={columns} data={data} rowKey="key" />
      </div>

      <Modal
        title="添加 API Token"
        visible={isModalVisible}
        onOk={handleAdd}
        onCancel={() => setIsModalVisible(false)}
        okText="确认"
        cancelText="取消"
      >
        <Input
          placeholder="请输入备注"
          value={remark}
          onChange={(value) => setRemark(value)}
        />
      </Modal>
    </>
  );
}
