export function Component() {
  const handleButtonClick = () => {
    window.location.href = '/gradio'; // 跳转到 /gradio 页面
  };

  return (
    <div className="ml-16 w-full max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">欢迎来到 Wav2Lip</h1>
      <p className="text-lg mb-4">
        Wav2Lip 是一个基于深度学习的语音到视频的转换工具。
      </p>
      <p className="text-lg mb-4">
        您可以在这里上传音频文件，然后选择一个视频文件，Wav2Lip 将会把音频文件的内容合成到视频文件中。
      </p>
      <h2 className="text-2xl font-semibold mb-4">演示地址</h2>
      <button
        className="px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-colors duration-300"
        onClick={handleButtonClick} // 点击按钮后跳转到 /gradio
      >
        访问演示
      </button>
    </div>
  );
}
