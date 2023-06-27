# from google.cloud import speech
from moviepy.editor import VideoFileClip
from pytube import YouTube
import os
import datetime
import io

from google.cloud import speech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/koei/Downloads/切り抜き/speech-to-text-project-389803-e9035bb1e4b0.json"

client = speech.SpeechClient()


# YouTubeの動画URLを指定
video_url = "https://www.youtube.com/watch?v=_yB5EpUg6HQ"

# YouTubeの動画をダウンロード
yt = YouTube(video_url)
stream = yt.streams.get_highest_resolution()  # 最高解像度のストリームを選択
video_path = stream.download(output_path='video')  # 動画を保存するパスを指定

# ダウンロードした動画のパスを取得ccdde
downloaded_video = VideoFileClip(video_path)

# 動画の開始と終了時間（秒）を指定
start_time = 0
end_time = 30

# 動画を切り取る
cut_video = downloaded_video.subclip(start_time, end_time)

output_path = 'cut_video.mp4'  # 保存先のパスを指定
cut_video.write_videofile(output_path, codec='libx264')

output_path2 = 'output_audio.wav'  # 出力音声ファイルのパスを指定

video = VideoFileClip(output_path)
audio = video.audio

audio.write_audiofile(output_path2)


# 切り取った動画を再生

# cut_video.preview()

# Google Cloudのサービスアカウントキーファイルへのパスを指定
# key_file = 'service_account_key.json'

# .mp4動画ファイルへのパスを指定
video_file = 'cut_video.mp4'


def transcribe_streaming(stream_file, keyword):
    """Streams transcription of the given audio file."""

    client = speech.SpeechClient()

    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="ja-JP",
        enable_word_time_offsets=True,
        #audio_channel_count=2
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    timestamps = []

    for response in responses:

        # print(response)

        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:

            # print(result)
            # print("Finished: {}".format(result.is_final))
            # print("Stability: {}".format(result.stability))

            # The alternatives are ordered from most likely to least.
            if result.alternatives:
                alternative = result.alternatives[0]
                transcript = alternative.transcript
                confidence = alternative.confidence
                # if alternative.words:
                if alternative.words and len(alternative.words) > 0:
                    start_time = alternative.words[0].start_time.seconds + \
                        (alternative.words[0].start_time.nanos / 1e9)

                    print(start_time.nanos)
                    end_time = alternative.words[-1].end_time.seconds + \
                        (alternative.words[-1].end_time.nanos/ 1e9)
                    if keyword.lower() in transcript.lower():
                        #timestamps.append((transcript, start_time, end_time, confidence))
                        timestamps.append((start_time, end_time))
    return timestamps


# キーワードとなるテキストを指定
keyword = 'アメリカ'

# キーワードの出現タイムスタンプを格納するリスト

timestamps = transcribe_streaming("./output_audio.wav", keyword)


for timestamp in timestamps:
    # transcript, start_time, end_time, confidence = timestamp
    start_time, end_time = timestamp
    # print("Transcript: {}".format(transcript))
    print("Start Time: {:.2f}".format(start_time))
    print("End Time: {:.2f}".format(end_time))
    # print("Confidence: {}".format(confidence))
    print()

# # クライアントの初期化
# client = speech.SpeechClient()

# # 音声認識の設定
# config = speech.RecognitionConfig(
#     encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#     sample_rate_hertz=16000,
#     language_code='ja-JP',
# )

# transcribe_streaming("./output_audio.wav")

# 音声ファイルの読み込みと処理
# with open(video_file, 'rb') as audio_file:
# content = audio_file.read()

# 音声認識リクエストの作成


# audio = speech.RecognitionAudio(content=content)

# operation=client.long_running_recognize(request={"config": config, "audio": audio})
# response = operation.recognize(config=config, audio=audio)


# キーワードのタイムスタンプを取得
# for response in responses
#     for result in response.results:
#         for word in result.alternatives[0].words:
#             if word.word.lower() == keyword.lower():
#                 start_time = word.start_time.seconds + word.start_time.nanos * 1e-9
#                 end_time = word.end_time.seconds + word.end_time.nanos * 1e-9
#                 timestamps.append((start_time, end_time))


# 結果の表示
# for timestamp in timestamps:
#     print(
#         f"キーワード '{keyword}' の出現タイムスタンプ: 開始時間={timestamp[0]}, 終了時間={timestamp[1]}")
