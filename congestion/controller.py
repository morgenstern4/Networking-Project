import time

class CongestionController:
    def __init__(self):
        self.cwnd = 1.0
        self.ssthresh = 16.0
        self.mode = "reno"
        self.last_loss_time = time.time()

    def set_mode(self, mode):
        print(f"🔁 Switching to algorithm: {mode.upper()}")
        self.mode = mode
        self.cwnd = 1.0
        self.ssthresh = 16.0
        self.last_loss_time = time.time()

    def on_ack(self):
        if self.mode == "reno":
            if self.cwnd < self.ssthresh:
                self.cwnd *= 2
            else:
                self.cwnd += 1
        elif self.mode == "tahoe":
            if self.cwnd < self.ssthresh:
                self.cwnd *= 2
            else:
                self.cwnd += 1 / self.cwnd
        elif self.mode == "cubic":
            T = time.time() - self.last_loss_time
            self.cwnd = 1 + (T - 1)**3
        elif self.mode == "bbr":
            self.cwnd = min(self.cwnd + 1, 100)

    def on_loss(self):
        self.ssthresh = max(self.cwnd / 2, 1)
        self.cwnd = 1.0
        self.last_loss_time = time.time()

    def get_cwnd(self):
        return int(max(1, self.cwnd))