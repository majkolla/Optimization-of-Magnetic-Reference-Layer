"""
param types cont, discrete etc 
"""

class Param: ... 

class ContinuousParam(Param): 
    pass 

class IntegerParam(Param): 
    pass 

class CategoricalParam(Param): 
    pass 

class SearchSpace: 
    """
    Holds the param and can pack and unpack helpers 
    """
    def __init__(self):
        pass
    def pack(self): 
        pass 
    def unpack(self): 
        pass 
    def clip(self): 
        pass 
    