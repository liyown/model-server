import axios from 'axios';
const instant = axios.create({
  baseURL: "http://127.0.0.1:1221/admin/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,  // 确保每次请求都带上 Cookie
});


instant.interceptors.request.use(
  (config) => {
    // 读取localStorage中的token
    const token = localStorage.getItem("token");
    if (token) {
      // 将token放入请求头中
      config.headers.set("Authorization", `${token}`)
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

instant.interceptors.response.use(
  (response) => {

    // 如果响应中有token，就更新localStorage中的token
    const token = response.headers["authorization"]
    if (token) {
      localStorage.setItem("token", token)
    }
    return response;
  },
  (error) => {
    if (error.response) {
      const statusCode = error.response.status;
      if (statusCode === 401) {
        // 401 未登录，跳转到登录页面
        console.error("未登录");
        // 跳转到登录页面
      } else {
        // 处理其他状态码
        console.error(`An error occurred: HTTP ${statusCode}`, error);
      }
    } else {
      // 处理没有响应的错误
      console.error("An error occurred:", error);
    }
    return Promise.reject(error);
  }
);


export default instant;
