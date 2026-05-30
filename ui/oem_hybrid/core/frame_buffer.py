from collections import deque


class FrameBuffer:

    def __init__(self, max_frames=2000):

        self.frames = deque(
            maxlen=max_frames
        )

    def add(self, frame):

        self.frames.appendleft(frame)

    def latest(self):

        return list(self.frames)