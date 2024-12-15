from gpiozero import MCP3008
from abc import ABC,abstractmethod

class Icds(ABC):
    @abstractmethod
    def get_brightness(self):
        pass

class Cds(Icds):
    def __init__(self):
        try:
            self.cds=MCP3008(channel=0)
        except Exception as e:
            print(f"初期化エラー: MCP3008のセットアップ中に問題が発生しました。詳細:{e}")
        

    
    def get_brightness(self):
        brightness=self.cds.value
        if brightness < 0 or brightness >1:
            raise ValueError("取得した値が異常範囲です。")
        return brightness