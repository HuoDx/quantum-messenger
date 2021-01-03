import pickle
import config

def save(obj: dict, filname: str):
    with open(config.data_path+'/%s.bin'%filname, 'wb') as fw:
        pickle.dump(obj, fw)
        fw.flush()
        
def load(filname: str, default) -> dict:
    try:
        with open(config.data_path+'/%s.bin'%filname, 'rb') as fr:
            obj = pickle.load(fr)
        return obj
    except FileNotFoundError:
        save(default, filname)
        return default

    
    
        
