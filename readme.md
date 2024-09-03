## ModelServer API 服务

### 服务框架

![](https://raw.githubusercontent.com/liyown/pic-go/master/blog/202409020952914.png)

#### 服务框架采用FastAPI
![](https://raw.githubusercontent.com/liyown/pic-go/master/blog/202409011832208.png)

#### 初步功能
- 模型推理API

![](https://raw.githubusercontent.com/liyown/pic-go/master/blog/202409011835010.png)
- 任务查询API

![](https://raw.githubusercontent.com/liyown/pic-go/master/blog/202409011837551.png)


### 后台管理系

采用React + Arco Design

#### 功能
- 管理APIToken, 增删改查
- 监控当前任务状态，获取排队任务数量
- 监控当前GPU状态，获取GPU使用情况, 内存使用情况

### 服务部署

**！！注意** 

在linux服务器部署前需要安装`python-dev`,否则oss下载和上传操作将会很慢

```shell
sudo apt-get install python-dev              
```