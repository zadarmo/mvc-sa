import moviepy.editor as mp
from moviepy.editor import VideoFileClip

def gif2mp4(input_path: str, output_path: str) -> None:
    """gif动图 -> mp4
    """
    clip = mp.VideoFileClip(input_path)
    clip.write_videofile(output_path)

def mp42gif(input_path: str, output_path: str) -> None:
    """mp4 -> gif动图 
    """
    clip = mp.VideoFileClip(input_path)
    clip.write_gif(output_path)


def speed_video(input_path: str, speed_rate: float, output_path: str) -> None:
    """倍速视频

    Parameters
    ----------
    input_path : str
        视频路径
    speed_rate : float
        倍速值
    output_path : str
        输出路径
    """
    video = VideoFileClip(input_path,audio=False)
    duration = video.duration
    video = video.fl_time(lambda t: speed_rate*t,
        apply_to=['mask','video','audio']
        ).set_end(duration/speed_rate)
    video.write_videofile(output_path, bitrate='2412k')