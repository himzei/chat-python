from pytubefix import YouTube
import os 

def get_video_and_audio(url):
    yt = YouTube(url)

    audio_stream = yt.streams.filter(only_audio=True).first()
    # 에러 처리
    if audio_stream is None:
        raise ValueError("오디오 스트림을 찾지 못했습니다.")
    
    audio_file_path = audio_stream.download(output_path="audio")
    print(f"오디오 파일 다운로드 완료: {audio_file_path}")

    video_stream = yt.streams.filter(only_video=True).first()
    video_file_path = video_stream.download(output_path="video")

    return audio_file_path, video_file_path


if __name__ == "__main__":
    url = input("YouTube 동영상 URL을 입력하세요: ")
    audio_file_path, video_file_path = get_video_and_audio(url)
    print(f"오디오 파일 경로: {audio_file_path}")
    print(f"비디오 파일 경로: {video_file_path}")