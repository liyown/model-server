from model.Wav2Lip.wav2lip_handle import Wav2LipInputModel
from fastapi import FastAPI
from gradio.routes import mount_gradio_app
import gradio as gr
import shutil
import os
from services.model_inference.wav2lip.model_service import video_with_audio_task_service

import librosa
import soundfile as sf
import numpy as np

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))

def lip_sync(video, audio, checkbox):

    # 开始对齐
    result = video_with_audio_task_service.face_handle.handle(Wav2LipInputModel.model_validate({
        "video_path": video,
        "audio_path": audio,
        "improve_video": checkbox
    }))

    result_vidio_path = os.path.join(current_dir, "result.mp4")

    # 将结果保存到临时文件
    with open(result_vidio_path, "wb") as f:
        f.write(result)
    
    return result_vidio_path




def create_gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Wav2Lip 在线演示")

        with gr.Row():
            with gr.Column():
                video_input = gr.Video(label="上传视频")
                audio_input = gr.Audio(label="上传音频", type="filepath")
                # 是否提高视频质量
                checkbox = gr.Checkbox(label="提高视频质量")
                sync_button = gr.Button("生成")

            with gr.Column():
                video_output = gr.Video(label="结果")

        sync_button.click(fn=lip_sync, inputs=[video_input, audio_input, checkbox], outputs=video_output)

    return demo

gradio_app = create_gradio_interface()
