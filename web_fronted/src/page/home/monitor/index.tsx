import { Statistic, Tag } from "@arco-design/web-react";
import { useEffect, useState } from "react";
import instant from "@/axios";

interface GpuStatus {
  load: number;
  name: string;
  memory_total: number;
  memory_used: number;
  memory_free: number;
  temperature: number;
}


export function Component() {
  const [taskCount, setTaskCount] = useState(0);
  const [gpuStatus, setGpuStatus] = useState<GpuStatus>({
    load: 0,
    name: "",
    memory_total: 0,
    memory_used: 0,
    memory_free: 0,
    temperature: 0
  });

  useEffect(() => {
    // 每2s更新一次数据
    setInterval(() => {
      // 获取数据
      instant.get("/task_count").then((res) => {
        if (res.status === 200) {
          setTaskCount(res.data.data.task_count);
        }
      });

      instant.get("/gpu_status").then((res) => {
        if (res.status === 200) {
          setGpuStatus(res.data.gpu_status[0]);
        }
      });
    }, 2000);
  },[]);


  return (
    <>
      <div
        className="flex-col justify-center align-center mt-12"
      >
        <div
          className="flex justify-center align-center"
        >
          <Statistic
            title="任务排队数量"
            value={taskCount}
          />
        </div>
         <div className="flex justify-center align-center mt-12">
            <Tag color="blue">GPU名称：{gpuStatus.name}</Tag>
         </div>
        <div className="flex justify-center align-center mt-12 ">
          <Statistic
            title="GPU使用率"
            value={Math.round(gpuStatus.load)}
            className="mx-12"
            suffix={"%"}
          />
          <Statistic
            title="GPU内存使用率"
            value={Math.round(gpuStatus.memory_used / gpuStatus.memory_total * 100)}
            className="mx-12"
            suffix={"%"}
          />
          <Statistic
            title="GPU温度"
            value={gpuStatus.temperature}
            className="mx-12"
            suffix={"℃"}
          />
        </div>
      </div>
    </>

  );
}

