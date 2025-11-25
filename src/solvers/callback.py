class Callback: 
    def on_start(self): pass 
    def on_step(self): pass 
    def on_end(self): pass 


class LoggingCallback(Callback): pass 
class EarlyStoppingCallback(Callback): pass  
class CheckpointCallback(Callback): pass 



