"""
:summary: 人脸识别处理模块
"""

from model.Interface import BaseHandle
from torchvision.models import resnet18
from PIL import Image
import torchvision.transforms as transforms
import torch
from torchvision.models.resnet import ResNet18_Weights
from pydantic import BaseModel


class FaceRecognitionCTX(BaseModel):
    image_path: str


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

    def preprocess(self, raw_data):
        """
        预处理输入数据
        """
        # 获取图片路径
        image_path = raw_data.image_path
        # 读取图片为tensor
        image = self.read_image(image_path)
        return image

    def inference(self, input_data):
        """
        执行推理
        """
        with torch.no_grad():
            output_data = self.model(input_data)
        return output_data

    def postprocess(self, output_data):
        """
        后处理输出数据,处理为可以返回的格式
        """
        # 获取预测结果，imageNet1000K分类
        _, predicted = torch.max(output_data, 1)
        return predicted.item()

    def handle(self, ctx: FaceRecognitionCTX):
        """
        处理数据
        """
        image = self.preprocess(ctx)
        output = self.inference(image)
        return self.postprocess(output)


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
    output = face_handle.handle(FaceRecognitionCTX(image_path="data/dog.png"))
    print(output)
