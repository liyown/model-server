"""
:summary: 人脸识别处理模块
"""

from model.Interface import BaseHandle
from torchvision.models import resnet18
from PIL import Image
import torchvision.transforms as transforms
import torch
from torchvision.models.resnet import ResNet18_Weights


class FaceRecognitionHandle(BaseHandle):
    """
    人脸识别处理类
    """

    def __init__(self):
        self.model = None

    def initialize(self, **kwargs):
        """
        初始化人脸识别模型
        """
        self.model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        self.model.eval()

    def preprocess(self, ctx):
        """
        预处理输入数据
        """
        # 获取图片路径
        image_path = ctx.get("image_path")
        # 读取图片为tensor
        image = self.read_image(image_path)
        ctx["image"] = image
        return ctx

    def inference(self, ctx):
        """
        执行推理
        """
        image = ctx.get("image")
        with torch.no_grad():
            output = self.model(image)
        ctx["output"] = output
        return ctx

    def postprocess(self, ctx):
        """
        后处理输出数据,处理为可以返回的格式
        """
        output = ctx.get("output")
        # 获取预测结果，imageNet1000K分类
        _, predicted = torch.max(output, 1)
        return predicted.item()


    def read_image(self, image_path):
        """
        读取图片为tensor
        """
        image = Image.open(image_path)
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
        ])
        image = transform(image)
        image = image.unsqueeze(0)
        return image


if __name__ == "__main__":
    face_handle = FaceRecognitionHandle()
    face_handle.initialize()
    ctx = {"image_path": "data/dog.png"}
    ctx = face_handle.preprocess(ctx)
    ctx = face_handle.inference(ctx)
    output = face_handle.postprocess(ctx)
    print(output)