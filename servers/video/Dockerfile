FROM debian:bullseye-slim

# Εγκατάσταση FFmpeg

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean

# Δημιουργία μη-root χρήστη

RUN useradd -m ffmpeguser

# Ορισμός φακέλου εργασίας

WORKDIR /videos

# Αντιγραφή του βίντεο

COPY video.mp4 /videos/

# Μετατροπή σε μη-root χρήστη

USER ffmpeguser

#CMD ["ffmpeg", "-re", "-stream_loop", "-1", "-i", "/videos/your_video.mp4", "-f", "null", "-", "-progress", "pipe:1"]

CMD ["ffmpeg", "-re", "-stream_loop", "-1", "-i", "/videos/video.mp4", "-f", "mpegts", "udp://224.0.0.1:1234", "-progress", "pipe:1"]
