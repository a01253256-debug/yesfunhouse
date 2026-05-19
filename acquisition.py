import socket
import struct
import threading
import time

gestures = [
    "Thumb up",
    "Extension of index and middle, flexion of the others",
    "Flexion of ring and little finger, extension of the others",
    "Thumb apposing base of little finger",
    "Abduction of all fingers",
    "Fingers flexed together in fist",
    "Pointing index",
    "Adduction of extended fingers",
    "Wrist supination (axis: middle finger)",
    "Wrist pronation (axis: middle finger)",
    "Wrist supination (axis: little finger)",
    "Wrist pronation (axis: little finger)",
    "Wrist flexion",
    "Wrist extension",
    "Wrist radial deviation",
    "Wrist ulnar deviation",
    "Wrist extension with closed hand"
]

class TrignoClient:
    def __init__(self, host, port_cmd, port_data):
        self.host = host
        self.port_cmd = port_cmd
        self.port_data = port_data
        self.sock_cmd = None
        self.sock_data = None
        self.emg_buffer = []
        self._collecting = False
        self._thread = None
        self._lock = threading.Lock()  # protege emg_buffer
        self.current_stimulus = 0   # 0 = rest, 1-17 = gesture
        self.current_rep = 0        # 0 = rest, 1-6 = rep
        self.restimulus_buffer = []
        self.rerepetition_buffer = []
        self.current_phase = "rest"   # or "contraction"
        self.current_gesture_name = ""
        self.time_remaining = 0.0

    # ... connect/disconnect/_recv_exact igual ...

    def _read_loop(self):
        while self._collecting:

            raw = self._recv_exact(64)
            values = struct.unpack('16f', raw)
            with self._lock:
                self.emg_buffer.append(values[:8])
                self.restimulus_buffer.append(self.current_stimulus)
                self.rerepetition_buffer.append(self.current_rep)

    def _start_stream(self):
        """Arranca UN solo thread de lectura."""
        self._collecting = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _stop_stream(self):
        """Para el thread y espera a que termine."""
        self._collecting = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def start_collection(self):
        # Arranca el stream UNA sola vez antes del loop
        print("Starting session. Get ready...")
        time.sleep(3.0)  # cuenta regresiva antes de empezar

        self._start_stream()

        for g_idx, g in enumerate(gestures):
            print(f"\n--- Gesto: {g} ---")
            self.current_stimulus = 0  # 0 = rest, 1-17 = gesture
            # Aquí iría la instrucción al sujeto (countdown, etc.)

            for r in range(6):
                self.current_rep = 0
                time.sleep(3.0)                 # rest — stimulus stays 0
                
                self.current_stimulus = g_idx + 1   # now 1-based, set BEFORE contraction
                self.current_rep = r + 1            # now 1-based
                time.sleep(5.0)                 # contraction
                     
            self.current_stimulus = 0           # back to rest between gestures

        self._stop_stream()
