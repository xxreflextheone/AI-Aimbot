# most credit for this goes to FS

import socket
import threading
import time
import sys
import re
import queue

try:
    from makcu import create_controller, MouseButton
    MAKCU_AVAILABLE = True
except ImportError:
    MAKCU_AVAILABLE = False
    print("[ERROR] makcu not found. Is the makcu library is installed?")
    sys.exit(1)

UDP_PORT = 5005
BUFFER_SIZE = 2048
MAX_QUEUE_SIZE = 2000

class InputHandler:
    def __init__(self):
        self.controller = None
        self.connected = False
        self.button_map = {
            'LEFT': MouseButton.LEFT,
            'RIGHT': MouseButton.RIGHT,
            'MIDDLE': MouseButton.MIDDLE
        }

        self.move_pattern = re.compile(r'^MOVE:(-?\d+),(-?\d+)$')
        self.click_pattern = re.compile(r'^CLICK:(LEFT|RIGHT|MIDDLE)$')
        self.scroll_pattern = re.compile(r'^SCROLL:(UP|DOWN)$')
        
        self.connect_to_macku()
        
        self.command_count = 0
        self.error_count = 0
        self._stop_event = threading.Event()
    
    def connect_to_macku(self):
        try:
            print("Connecting to Macku...")
            self.controller = create_controller()
            self.connected = True
            print("[SUCCESS] Connected to Macku")
            time.sleep(0.002)
        except Exception as e:
            print(f"[ERROR] Failed to connect to Macku: {e}")
            self.connected = False
    
    def process_command_batch(self, commands):
        if not self.connected:
            return False
        
        success_count = 0
        agg_dx = 0
        agg_dy = 0
        others = []
        for command in commands:
            if command.startswith('MOVE:'):
                m = self.move_pattern.match(command)
                if m:
                    agg_dx += int(m.group(1))
                    agg_dy += int(m.group(2))
            else:
                others.append(command)

        if agg_dx != 0 or agg_dy != 0:
            if self._execute_single_command(f"MOVE:{agg_dx},{agg_dy}"):
                success_count += 1

        for command in others:
            if self._execute_single_command(command):
                success_count += 1
        
        return success_count > 0
    
    def _execute_single_command(self, message):
        try:
            self.command_count += 1
            
            if message.startswith('MOVE:'):
                match = self.move_pattern.match(message)
                if match:
                    dx, dy = int(match.group(1)), int(match.group(2))
                    # Validate reasonable movement bounds
                    if abs(dx) <= 2000 and abs(dy) <= 2000:
                        self.controller.mouse.move(dx, dy)
                        return True
            
            elif message.startswith('CLICK:'):
                match = self.click_pattern.match(message)
                if match:
                    button_name = match.group(1)
                    button = self.button_map[button_name]
                    self.controller.mouse.press(button)
                    time.sleep(0.001)
                    self.controller.mouse.release(button)
                    return True
            
            elif message.startswith('SCROLL:'):
                match = self.scroll_pattern.match(message)
                if match:
                    direction = match.group(1)
                    scroll_delta = 1 if direction == 'UP' else -1
                    self.controller.mouse.scroll(scroll_delta)
                    return True
            
            self.error_count += 1
            return False
            
        except Exception as e:
            self.error_count += 1
            if self.command_count % 100 == 0:
                print(f"[ERROR] Command failed: {e}")
            return False

class InputListener:
    def __init__(self, port=UDP_PORT):
        self.port = port
        self.sock = None
        self.running = False
        self.input_handler = InputHandler()
        self.command_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self.batch_size = 50
        self.batch_timeout = 0.002
        self._stop_event = threading.Event()
        
    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.sock.settimeout(0.01)
            self.sock.bind(("0.0.0.0", self.port))
            self.running = True
            
            print(f"[READY] listening on UDP port {self.port}")
            
            self._receiver_thread = threading.Thread(target=self._optimized_receive_loop, daemon=True)
            self._processor_thread = threading.Thread(target=self._batch_processor_loop, daemon=True)
            
            self._receiver_thread.start()
            self._processor_thread.start()
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start listener: {e}")
            return False
    
    def stop(self):
        self.running = False
        self._stop_event.set()
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

        try:
            if hasattr(self, '_receiver_thread'):
                self._receiver_thread.join(timeout=0.5)
            if hasattr(self, '_processor_thread'):
                self._processor_thread.join(timeout=0.5)
        except Exception:
            pass

        print("[INFO] listener stopped.")
    
    def _optimized_receive_loop(self):
        consecutive_errors = 0
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8').strip()

                if not self.command_queue.full():
                    self.command_queue.put_nowait(message)
                    consecutive_errors = 0
                else:
                    try:
                        self.command_queue.get_nowait()
                        self.command_queue.put_nowait(message)
                    except queue.Empty:
                        pass
                
            except socket.timeout:
                consecutive_errors = 0
                continue
            except Exception as e:
                consecutive_errors += 1
                if self.running and consecutive_errors < 10:
                    time.sleep(0.0005)
                elif consecutive_errors >= 10:
                    print(f"[ERROR] Too many receive errors, pausing: {e}")
                    time.sleep(0.005)
                    consecutive_errors = 0

            if self._stop_event.is_set():
                break
    
    def _batch_processor_loop(self):
        while self.running:
            if self._stop_event.is_set():
                break
            commands = []
            start_time = time.time()
            
            try:
                while len(commands) < self.batch_size and (time.time() - start_time) < self.batch_timeout:
                    try:
                        command = self.command_queue.get_nowait()
                        commands.append(command)
                    except queue.Empty:
                        try:
                            command = self.command_queue.get(timeout=0.0005)
                            commands.append(command)
                        except queue.Empty:
                            break

                if commands:
                    self.input_handler.process_command_batch(commands)
                    
                    for _ in commands:
                        try:
                            self.command_queue.task_done()
                        except ValueError:
                            pass
                
                if not commands:
                    time.sleep(0.00005)
            except Exception as e:
                print(f"[ERROR] Batch processing error: {e}")
                time.sleep(0.001)

def main():
    if not MAKCU_AVAILABLE:
        print("[ERROR] Macku module not available. Exiting.")
        return
    
    listener = InputListener()
    
    if not listener.start():
        print("[ERROR] Failed to start listener")
        return
    
    try:
        print("\nPress Ctrl+C to stop\n")
        last_stats_time = time.time()
        
        while True:
            time.sleep(1)
            current_time = time.time()
            if current_time - last_stats_time >= 10:
                handler = listener.input_handler
                if handler.command_count > 0:
                    error_rate = (handler.error_count / handler.command_count) * 100
                    print(f"[STATS] Commands: {handler.command_count}, Error rate: {error_rate:.1f}%")
                last_stats_time = current_time
            
    except KeyboardInterrupt:
        print("\n[INFO] Stopping..")
        listener.stop()

if __name__ == "__main__":
    main()
